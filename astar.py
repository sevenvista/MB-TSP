import heapq
from typing import List, Tuple, Optional, Set
from models import EType, Cell


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(pos: Tuple[int, int], rows: int, cols: int) -> List[Tuple[int, int]]:
    """Get valid neighboring positions (4-directional)"""
    row, col = pos
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < rows and 0 <= new_col < cols:
            neighbors.append((new_row, new_col))
    return neighbors


def astar_pathfinding(
    grid: List[List[Cell]], 
    start_pos: Tuple[int, int], 
    end_pos: Tuple[int, int]
) -> Optional[int]:
    """
    A* pathfinding algorithm to find shortest distance between two points
    Returns the distance (number of steps) or None if no path exists
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Priority queue: (f_score, g_score, position)
    open_set = [(0, 0, start_pos)]
    came_from = {}
    g_score = {start_pos: 0}
    f_score = {start_pos: heuristic(start_pos, end_pos)}
    closed_set: Set[Tuple[int, int]] = set()
    
    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
            
        if current == end_pos:
            return g_score[current]
        
        closed_set.add(current)
        
        for neighbor in get_neighbors(current, rows, cols):
            row, col = neighbor
            
            # Check if neighbor is walkable
            if grid[row][col].type == EType.OBSTACLE:
                continue
            
            if neighbor in closed_set:
                continue
            
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f = tentative_g_score + heuristic(neighbor, end_pos)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, tentative_g_score, neighbor))
    
    return None  # No path found
