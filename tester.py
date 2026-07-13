"""
O módulo tester executa e orquestra a medição de desempenho (benchmark) de múltiplos
modelos de recomendação e processamento de eventos.
"""
from __future__ import annotations

import gc
import importlib.util
import io
import os
import random
import sys
import time
import contextlib
from typing import Final
import multiprocessing

def run_benchmark_worker(
    py_file: str,
    events: list[tuple[int, int]],
    k: int,
    target_user: int,
    result_queue: multiprocessing.Queue[tuple[str, float] | tuple[str, str]],
) -> None:
    """
    Executa o benchmark de um arquivo de modelo específico em um processo isolado.

    O isolamento em subprocesso garante que limites rígidos de tempo de execução
    (timeout) possam ser aplicados e que vazamentos de memória ou efeitos colaterais
    de um modelo não afetem a execução dos demais.

    Args:
        py_file (str): Caminho absoluto ou relativo para o arquivo de script do modelo.
        events (list[tuple[int, int]]): Lista de eventos de entrada estruturados como tuplas (usuário, item).
        k (int): Quantidade de recomendações a serem geradas.
        target_user (int): O identificador do usuário de destino do benchmark.
        result_queue (multiprocessing.Queue): Fila de multiprocessamento para retorno do status e resultados.
    """
    module_name: str = os.path.splitext(os.path.basename(py_file))[0]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                result_queue.put(("ERROR", "Spec loader not found"))
                return
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

        if hasattr(module, "process_events"):
            gc.collect()
            start_time: float = time.perf_counter()
            with contextlib.redirect_stdout(io.StringIO()):
                module.process_events(events, k, target_user)
            elapsed_time: float = time.perf_counter() - start_time
            result_queue.put(("SUCCESS", elapsed_time))
        else:
            result_queue.put(("ERROR", "process_events not found"))
    except Exception as error:
        result_queue.put(("ERROR", str(error)))

from excel_exporter import BenchmarkResult, export_results_to_excel

if __name__ == "__main__":
    multiprocessing.freeze_support()

    num_users: Final[int] = 100_000
    k: Final[int] = 10
    target_user: Final[int] = 42
    max_allowed_time: Final[float] = 10.0

    event_sizes: Final[list[int]] = [10_000, 50_000, 250_000, 1_250_000, 6_250_000]

    modelos_dir = "modelos"
    py_files: list[str] = sorted(
        [
            os.path.join(modelos_dir, f)
            for f in os.listdir(modelos_dir)
            if f.endswith(".py")
        ]
    )

    results_data: list[BenchmarkResult] = []
    slow_files: set[str] = set()

    print("Iniciando benchmark com limite rígido de 10s...")
    print(f"Arquivos a testar: {', '.join(os.path.basename(f) for f in py_files)}")
    print("-" * 80)

    for round_num, num_events in enumerate(event_sizes, 1):
        print(f"\nRodada {round_num}/5 | Eventos: {num_events:,}")
        print("-" * 80)

        random.seed(42)
        events: list[tuple[int, int]] = [
            (random.randint(1, num_users), random.randint(1, 1000))
            for _ in range(num_events)
        ]

        for py_file in py_files:
            file_name = os.path.basename(py_file)
            if file_name in slow_files:
                print(f"{file_name} | Pulado (Eliminado em rodada anterior)")
                results_data.append(
                    BenchmarkResult(
                        arquivo=file_name,
                        eventos=num_events,
                        tempo_total="",
                        throughput="",
                        status="Pulado",
                    )
                )
                continue

            result_queue: multiprocessing.Queue[
                tuple[str, float] | tuple[str, str]
            ] = multiprocessing.Queue()

            process: multiprocessing.Process = multiprocessing.Process(
                target=run_benchmark_worker,
                args=(py_file, events, k, target_user, result_queue),
            )

            start_real: float = time.perf_counter()
            process.start()
            process.join(timeout=max_allowed_time)

            status: str = "OK"
            elapsed: float = 0.0
            throughput: float = 0.0
            elapsed_str: str | float = ""
            throughput_str: str | float = ""

            if process.is_alive():
                process.terminate()
                process.join()
                slow_files.add(file_name)
                status = "Eliminado (>10s)"
                print(f"{file_name} | [ELIMINADO >10s (TIMEOUT)]")
            else:
                if not result_queue.empty():
                    res_type, res_val = result_queue.get()
                    if res_type == "SUCCESS":
                        elapsed = float(res_val)
                        throughput = num_events / elapsed

                        if elapsed > max_allowed_time:
                            print(
                                f"{file_name} | Tempo: {elapsed:.3f}s | Throughput: {throughput:,.0f} ev/s [ELIMINADO >10s]"
                            )
                            slow_files.add(file_name)
                            status = "Eliminado (>10s)"
                        else:
                            print(
                                f"{file_name} | Tempo: {elapsed:.3f}s | Throughput: {throughput:,.0f} ev/s [OK]"
                            )
                            status = "OK"

                        elapsed_str = round(elapsed, 4)
                        throughput_str = round(throughput, 1)
                    else:
                        print(f"{file_name} | Erro ao executar: {res_val}")
                        status = f"Erro: {res_val}"
                else:
                    print(f"{file_name} | Erro: Processo morreu ou não retornou dados.")
                    status = "Erro desconhecido"

            results_data.append(
                BenchmarkResult(
                    arquivo=file_name,
                    eventos=num_events,
                    tempo_total=elapsed_str,
                    throughput=throughput_str,
                    status=status,
                )
            )

    excel_filename: str = "resultados_benchmark.xlsx"
    try:
        export_results_to_excel(results_data, excel_filename)
        print(
            f"\nResultados salvos com sucesso em '{excel_filename}' (Pronto para abrir no Excel)!"
        )
    except Exception as error:
        print(f"\nErro ao salvar a planilha Excel: {error}")