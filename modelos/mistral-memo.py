def process_events(events: list[tuple[int, int]], k: int, target_user_id: int) -> list[tuple[list[tuple[int, int]], int]]:
    scores = {}
    top_k = []

    for event in events:
        user_id, score = event

        # Atualize o score acumulado do usuário
        if user_id in scores:
            scores[user_id] += score
        else:
            scores[user_id] = score

        # Verifique se o target_user_id está no top-K e retorne sua posição
        if len(top_k) < k and (target_user_id not in scores or scores.get(target_user_id, 0) > (scores[top_k[-1][0]] if top_k else 0)):
            top_k.append((target_user_id, scores.get(target_user_id, 0)))
            top_k.sort(key=lambda x: x[1], reverse=True)

    # Retorne os top-K usuários
    return [(top_k[:k], len(top_k) + 1 if target_user_id in scores else -1)]
