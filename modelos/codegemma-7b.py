from collections import defaultdict
from heapq import heappop, heappush

class Ranking:
    def __init__(self, k):
        self.k = k
        self.scores = defaultdict(int)
        self.heap = []

    def update(self, user_id, score):
        self.scores[user_id] += score
        if len(self.heap) < self.k:
            heappush(self.heap, (-self.scores[user_id], user_id))
        else:
            if -self.scores[user_id] > self.heap[0][0]:
                heappop(self.heap)
                heappush(self.heap, (-self.scores[user_id], user_id))

    def get_top_k(self):
        return sorted([(score, user_id) for score, user_id in self.heap], reverse=True)

    def get_rank(self, target_user_id):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return next((i for i, (user_id, _) in enumerate(sorted_scores) if user_id == target_user_id), None)

def process_events(events, k, target_user_id):
    ranking = Ranking(k)

    results = []
    for user_id, score in events:
        ranking.update(user_id, score)
        top_k = ranking.get_top_k()
        rank = ranking.get_rank(target_user_id)
        results.append((top_k, rank))

    return results
