from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterator
from typing import Final, List, Tuple, Dict, TypeVar, Generic, Protocol, Literal
import heapq
import bisect

# Definindo tipos para facilitar a leitura do código
T = TypeVar("T", bound="Comparable")
K = TypeVar("K", bound=int)

class Comparable(Protocol):
    def __lt__(self, other: object) -> bool: ...

# Definindo uma estrutura para armazenar as informações do usuário
@dataclass(slots=True)
class UserScore:
    user_id: int
    score: int

    def __lt__(self, other: UserScore) -> bool:
        if self.score != other.score:
            return self.score < other.score
        return self.user_id > other.user_id

# Função auxiliar para manter o heap de top-K atualizado
def update_top_k(user_scores: List[UserScore], k: int, new_score: UserScore) -> None:
    if len(user_scores) < k:
        heapq.heappush(user_scores, new_score)
    else:
        heapq.heappushpop(user_scores, new_score)

# Função principal para processar eventos
def process_events(
    events: list[tuple[int, int]],
    k: int,
    target_user_id: int
) -> list[tuple[list[tuple[int, int]], int]]:
    user_scores: Dict[int, UserScore] = {}
    top_k_users: List[UserScore] = []
    
    results = []
    
    for event in events:
        user_id, score = event
        
        if user_id not in user_scores:
            user_scores[user_id] = UserScore(user_id, 0)
        
        user_scores[user_id].score += score
        
        new_score = UserScore(user_id, user_scores[user_id].score)
        update_top_k(top_k_users, k, new_score)
        
        top_k = sorted([(s.user_id, s.score) for s in top_k_users], key=lambda x: (-x[1], x[0]))
        target_rank = get_target_rank(top_k_users, target_user_id)
        
        results.append((top_k, target_rank))
    
    return results

# Função para obter o rank do usuário alvo
def get_target_rank(top_k_users: List[UserScore], user_id: int) -> int:
    if not top_k_users:
        return -1
    
    sorted_scores = sorted([(s.user_id, s.score) for s in top_k_users], key=lambda x: (-x[1], x[0]))
    rank = 1
    for user, score in sorted_scores:
        if user == user_id:
            return rank
        rank += 1
    
    return -1

# Exemplo de uso
events = [(1, 10), (2, 20), (1, 5), (3, 30), (4, 15)]
k = 3
target_user_id = 1
result = process_events(events, k, target_user_id)
for top_k, rank in result:
    print("Top-K Users:", top_k)
    print("Target User Rank:", rank)
