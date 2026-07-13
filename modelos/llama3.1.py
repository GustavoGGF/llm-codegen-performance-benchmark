from typing import List, Tuple, TypeVar

T = TypeVar('T')

def process_events(events: List[Tuple[int, int]], k: int, target_user_id: int) -> List[Tuple[List[Tuple[int, int]], int]]:
    """
    Processa um stream de eventos e retorna os top-K usuários após cada atualização,
    bem como a posição do usuário-alvo no ranking global.

    :param events: lista de eventos (user_id, score)
    :param k: número de usuários para retornar nos top-K
    :param target_user_id: ID do usuário-alvo
    :return: lista de tuplas (top_k, target_rank) para cada evento
    """
    user_scores = {}  # dicionário para armazenar os scores dos usuários

    result = []  # resultado final com as listas de top-k e a posição do usuário-alvo
    for event in events:
        user_id, score = event
        if user_id not in user_scores:
            user_scores[user_id] = 0  # inicializa o score para 0 se não existe

        # atualiza o score do usuário
        user_scores[user_id] += score

        # prepara a lista de top-k e a posição do usuário-alvo
        top_k = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        target_rank = get_target_rank(top_k, target_user_id)

        result.append((top_k, target_rank))

    return result


def get_target_rank(top_k: List[Tuple[int, int]], target_user_id: int) -> int:
    """
    Encontra a posição do usuário-alvo no ranking top-k.

    :param top_k: lista de usuários ordenados pelo score
    :param target_user_id: ID do usuário-alvo
    :return: posição do usuário-alvo no ranking top-k (1-indexado)
    """
    for i, (user_id, _) in enumerate(top_k):
        if user_id == target_user_id:
            return i + 1

    # se o usuário não está no top-k, retorna -1
    return -1
