import sys
from collections import defaultdict
from typing import DefaultDict, List, Tuple


def process_events(
    events: list[tuple[int, int]], k: int, target_user_id: int
) -> List[Tuple[List[Tuple[int, int]], int]]:

    top_k = defaultdict(list)  # top-k users by score for each event
    ranks = []  # rank of target_user_id for each event
    score = defaultdict(int)  # current user's score

    for i, (user_id, user_score) in enumerate(events):
        score[user_id] += user_score

        if len(top_k[i]) < k:
            top_k[i].append((user_score, user_id))
        elif top_k[i][-1][0] <= user_score:
            top_k[i].pop()
            top_k[i].append((user_score, user_id))

        ranks.append(
            binarySearch(
                score[user_id], sorted([x for _, x in top_k[i]]), target_user_id, k
            )
        )

    return [(sorted(top_k[i]), ranks[i]) for i in range(len(events))]


def binarySearch(score: int, top_k: List[int], target_user_id: int, k: int) -> int:
    if score not in top_k and len(top_k) == k:
        return -1

    low, high = 0, len(top_k) - 1
    while low <= high:
        mid = (low + high) >> 1

        if target_user_id < top_k[mid]:
            high = mid - 1

        elif target_user_id > top_k[mid]:
            low = mid + 1

        else:
            return mid

    return -1


if __name__ == "__main__":
    lines = sys.stdin.readlines()
    events, k, target_user_id = eval(lines[0]), int(lines[2]), int(lines[4])

    for top_k, rank in process_events(events, k, target_user_id):
        print(f"({top_k}, {rank})")
