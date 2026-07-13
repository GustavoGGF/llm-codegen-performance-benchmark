from collections import deque
from typing import List, Tuple

def process_events(events: List[Tuple[int, int]], k: int, target_user_id: int) -> List[Tuple[List[Tuple[int, int]], int]]:
    # Initialize a priority queue for the top-k users
    pq = deque([], maxlen=k+1)

    # Iterate over each event
    for user_id, score in events:
        # Update the current score for this user
        current_score = score

        # Check if the user is already in the priority queue
        if user_id in pq:
            # If so, update their current score and reinsert them into the queue
            index = pq.index(user_id)
            pq[index] = (current_score, user_id)
        else:
            # If not, insert a new entry for this user at the appropriate position in the queue
            pq.append((current_score, user_id))

        # Trim the priority queue to the correct size
        while len(pq) > k:
            pq.pop()

    # Return the top-k users and their scores
    return [(user_id, current_score) for score, user_id in pq]
