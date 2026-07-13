from __future__ import annotations
from collections import defaultdict
from typing import List, Tuple, Dict, Counter, Optional

def process_events(events: List[Tuple[int, int]], k: int, target_user_id: int) -> List[Tuple[List[Tuple[int, int]], Optional[int]]]:
    scores = defaultdict(lambda: 0)
    top_k_scores: Counter[int] = Counter()
    result = []

    for user_id, score in events:
        prev_score = scores[user_id]
        new_score = prev_score + score
        scores[user_id] = new_score

        # Atualiza o top-k
        if prev_score > 0:
            top_k_scores[prev_score] -= 1
        top_k_scores[new_score] += 1

        top_users = sorted(top_k_scores.most_common(), key=lambda x: (-x[1], -x[0]))[:k]

        # Calcula a posição do target_user_id
        target_rank = None
        for rank, (user_id, score) in enumerate(top_users):
            if user_id == target_user_id:
                target_rank = rank + 1
                break

        result.append((top_users[:k], target_rank))

    return result
