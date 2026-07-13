from __future__ import annotations
import heapq
from collections import defaultdict
from typing import List, Tuple

def process_events(
    events: List[Tuple[int, int]],
    k: int,
    target_user_id: int
) -> List[Tuple[List[Tuple[int, int]], int]]:

    user_scores = defaultdict(int)
    score_board = []
    results = []

    for user_id, score in events:
        user_scores[user_id] += score
        heapq.heappush(score_board, (-user_scores[user_id], user_id))
        if len(score_board) > k:
            heapq.heappop(score_board)

        top_k = [(-score, uid) for score, uid in sorted(score_board)]
        target_rank = -1
        if target_user_id in user_scores:
            target_score = user_scores[target_user_id]
            target_rank = 1 + sum(
                1 for uid, score in user_scores.items()
                if score > target_score or (score == target_score and uid < target_user_id)
            )
        results.append((top_k, target_rank))
    return results
