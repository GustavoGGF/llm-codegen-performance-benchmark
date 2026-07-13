from typing import List, Tuple
import heapq
from collections import defaultdict

class UserScore:
    def __init__(self, user_id: int, score: int):
        self.user_id = user_id
        self.score = score

    def __lt__(self, other):
        return self.score < other.score or (self.score == other.score and self.user_id > other.user_id)
    
def process_events(events: List[Tuple[int, int]], k: int, target_user_id: int) -> List[Tuple[List[Tuple[int, int]], int]]:
    user_scores = defaultdict(int)  # dict to store all users scores
    heap = []  # min-heap to store top K scores
    result = []
    
    for user_id, score in events:
        old_score = user_scores[user_id]
        new_score = UserScore(user_id, old_score + score)
        
        # If we have more than k users in the heap, remove the smallest one
        if len(heap) == k and new_score > heap[0]:
            heapq.heappop(heap)
            
        # If there's still space or this user has a larger score then push it to the heap
        if len(heap) < k or new_score > heap[0]:
            heapq.heappush(heap, new_score)
        
        user_scores[user_id] += score
        # Sort the heap and keep only top K users
        heap = sorted(heap, reverse=True)[:k]
        
        # Calculate rank for target_user_id 
        target_rank = 1 + len([score for score in heap if score.score > user_scores[target_user_id] or (score.score == user_scores[target_user_id] and score.user_id < target_user_id)])
        
        result.append(([(user.user_id, user.score) for user in heap], target_rank))
    
    return result
