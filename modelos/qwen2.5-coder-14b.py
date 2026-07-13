from __future__ import annotations

import heapq
from collections.abc import Sequence
from typing import Final, Protocol, TypeVar

T = TypeVar("T")

class Comparable(Protocol):
    def __lt__(self, other: object) -> bool: ...

def binary_search(sorted_list: list[Comparable], target: Comparable) -> int:
    low, high = 0, len(sorted_list) - 1
    while low <= high:
        mid = (low + high) >> 1
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

class UserScore(Protocol):
    user_id: int
    score: int

def process_events(
    events: Sequence[tuple[int, int]],
    k: int,
    target_user_id: int
) -> list[tuple[list[tuple[int, int]], int]]:
    user_scores: dict[int, int] = {}
    top_k_heap: list[UserScore] = []
    target_rank: int = -1

    def update_and_get_rank(user_id: int, score: int) -> tuple[list[tuple[int, int]], int]:
        nonlocal user_scores, top_k_heap, target_rank

        if user_id in user_scores:
            old_score = user_scores[user_id]
            user_scores[user_id] += score
            new_score = user_scores[user_id]

            # Remove the old entry from the heap
            index = binary_search(top_k_heap, (old_score, user_id))
            if index != -1:
                del top_k_heap[index]

        else:
            user_scores[user_id] = score
            new_score = user_scores[user_id]

        # Add the new or updated entry to the heap
        heapq.heappush(top_k_heap, (-new_score, user_id))

        # Keep the heap size at k
        if len(top_k_heap) > k:
            heapq.heappop(top_k_heap)

        # Sort the top-k heap by score descending for output
        sorted_top_k = [(-score, user_id) for _, (score, user_id) in enumerate(sorted(top_k_heap))]

        # Determine the rank of the target user
        if target_user_id in user_scores:
            target_rank = binary_search(top_k_heap, (-user_scores[target_user_id], target_user_id))
            if target_rank != -1:
                target_rank += 1  # Convert to 1-based index

        return sorted_top_k, target_rank

    results: list[tuple[list[tuple[int, int]], int]] = []
    for event in events:
        user_id, score = event
        top_k, rank = update_and_get_rank(user_id, score)
        results.append((top_k, rank))

    return results
