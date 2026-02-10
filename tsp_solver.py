"""
TSP Solver using modern heuristic algorithms.

Implements efficient approximation algorithms for the Traveling Salesman Problem:
- Nearest Neighbor (constructive heuristic)
- 2-opt improvement (pairwise exchange)
- 3-opt improvement (k-opt heuristic)

Based on algorithms from:
https://en.wikipedia.org/wiki/Travelling_salesman_problem

These heuristics provide near-optimal solutions (typically within 2-5% of optimal)
while being computationally efficient enough for large problem instances.
"""
from typing import List, Dict, Tuple, Optional
import itertools
import random


def solve_tsp(
    distances: Dict[Tuple[str, str], int],
    points: List[str]
) -> Optional[List[str]]:
    """
    Solve Traveling Salesman Problem using modern heuristic algorithms.
    
    Strategy:
    - Very small (≤7): Brute force for optimal solution
    - Small (≤10): Nearest neighbor + 2-opt improvement
    - Medium/Large (>10): Multiple nearest neighbor starts + 2-opt + 3-opt
    
    Based on algorithms from:
    https://en.wikipedia.org/wiki/Travelling_salesman_problem
    
    Args:
        distances: Dictionary mapping (from_id, to_id) to distance
        points: List of point IDs to visit
    
    Returns:
        Near-optimal path as list of point IDs, or None if no valid path exists
    """
    if not points:
        return []
    
    if len(points) == 1:
        return points
    
    # For very small problems (≤7 points), use brute force for optimal solution
    if len(points) <= 7:
        return solve_tsp_bruteforce(distances, points)
    
    # For small to medium problems, use nearest neighbor + 2-opt
    elif len(points) <= 10:
        initial_path = solve_tsp_nearest_neighbor(distances, points)
        if initial_path is None:
            return None
        return improve_with_2opt(distances, initial_path)
    
    # For larger problems, use multiple starts with 2-opt and 3-opt
    else:
        return solve_tsp_heuristic(distances, points)


def solve_tsp_bruteforce(
    distances: Dict[Tuple[str, str], int],
    points: List[str]
) -> Optional[List[str]]:
    """Brute force TSP solver"""
    best_path = None
    best_distance = float('inf')
    
    # Try all permutations
    for perm in itertools.permutations(points):
        path_list = list(perm)
        total_distance = 0
        valid = True
        
        # Calculate total distance for this permutation
        for i in range(len(path_list) - 1):
            key = (path_list[i], path_list[i + 1])
            if key in distances:
                total_distance += distances[key]
            else:
                # Try reverse direction
                reverse_key = (path_list[i + 1], path_list[i])
                if reverse_key in distances:
                    total_distance += distances[reverse_key]
                else:
                    valid = False
                    break
        
        if valid and total_distance < best_distance:
            best_distance = total_distance
            best_path = path_list
    
    return best_path


def solve_tsp_nearest_neighbor(
    distances: Dict[Tuple[str, str], int],
    points: List[str],
    start_point: Optional[str] = None
) -> Optional[List[str]]:
    """
    Nearest neighbor heuristic for TSP.
    Greedy algorithm that visits the nearest unvisited city at each step.
    
    Args:
        distances: Distance dictionary
        points: List of points to visit
        start_point: Optional starting point (defaults to first point)
    
    Returns:
        Path visiting all points, or None if no valid path exists
    """
    if not points:
        return []
    
    unvisited = set(points)
    start = start_point if start_point in points else points[0]
    path = [start]
    unvisited.remove(start)
    
    while unvisited:
        current = path[-1]
        nearest = None
        nearest_dist = float('inf')
        
        for point in unvisited:
            dist = get_distance(distances, current, point)
            
            if dist is not None and dist < nearest_dist:
                nearest_dist = dist
                nearest = point
        
        if nearest is None:
            # No valid path found
            return None
        
        path.append(nearest)
        unvisited.remove(nearest)
    
    return path


def solve_tsp_heuristic(
    distances: Dict[Tuple[str, str], int],
    points: List[str]
) -> Optional[List[str]]:
    """
    Advanced heuristic combining multiple strategies:
    1. Try multiple nearest neighbor starting points
    2. Apply 2-opt improvement
    3. Apply 3-opt improvement on best result
    
    This gives near-optimal results for large problems.
    """
    best_path = None
    best_distance = float('inf')
    
    # Try nearest neighbor from multiple starting points
    num_starts = min(len(points), 5)  # Try up to 5 different starts
    start_indices = [0] + random.sample(range(1, len(points)), min(num_starts - 1, len(points) - 1))
    
    for start_idx in start_indices:
        path = solve_tsp_nearest_neighbor(distances, points, points[start_idx])
        if path is None:
            continue
        
        # Apply 2-opt improvement
        path = improve_with_2opt(distances, path)
        
        # Calculate total distance
        path_distance = calculate_path_distance(distances, path)
        if path_distance is not None and path_distance < best_distance:
            best_distance = path_distance
            best_path = path
    
    if best_path is None:
        return None
    
    # Apply 3-opt improvement on the best path found
    # (only for moderate sizes, as 3-opt is expensive)
    if len(points) <= 50:
        best_path = improve_with_3opt(distances, best_path)
    
    return best_path


def get_distance(
    distances: Dict[Tuple[str, str], int],
    from_point: str,
    to_point: str
) -> Optional[int]:
    """Get distance between two points, trying both directions"""
    key1 = (from_point, to_point)
    key2 = (to_point, from_point)
    
    if key1 in distances:
        return distances[key1]
    elif key2 in distances:
        return distances[key2]
    return None


def calculate_path_distance(
    distances: Dict[Tuple[str, str], int],
    path: List[str]
) -> Optional[int]:
    """Calculate total distance of a path"""
    if not path or len(path) < 2:
        return 0
    
    total = 0
    for i in range(len(path) - 1):
        dist = get_distance(distances, path[i], path[i + 1])
        if dist is None:
            return None
        total += dist
    
    return total


def improve_with_2opt(
    distances: Dict[Tuple[str, str], int],
    path: List[str],
    max_iterations: int = 1000
) -> List[str]:
    """
    2-opt improvement algorithm.
    
    Iteratively removes two edges and reconnects the path in a different way
    if it results in a shorter tour. This is one of the most effective and
    widely used local search heuristics for TSP.
    
    Reference: https://en.wikipedia.org/wiki/Travelling_salesman_problem#Pairwise_exchange
    
    Args:
        distances: Distance dictionary
        path: Initial path
        max_iterations: Maximum number of iterations without improvement
    
    Returns:
        Improved path
    """
    improved = True
    iterations = 0
    best_path = path[:]
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(len(best_path) - 1):
            for j in range(i + 2, len(best_path)):
                # Try swapping edges (i, i+1) and (j, j+1)
                # Current: ... -> path[i] -> path[i+1] -> ... -> path[j] -> path[j+1] -> ...
                # New: ... -> path[i] -> path[j] -> ... -> path[i+1] -> path[j+1] -> ...
                
                # Calculate current distance
                current_dist = 0
                d1 = get_distance(distances, best_path[i], best_path[i + 1])
                if d1 is None:
                    continue
                current_dist += d1
                
                if j + 1 < len(best_path):
                    d2 = get_distance(distances, best_path[j], best_path[j + 1])
                    if d2 is None:
                        continue
                    current_dist += d2
                
                # Calculate new distance after 2-opt swap
                new_dist = 0
                d3 = get_distance(distances, best_path[i], best_path[j])
                if d3 is None:
                    continue
                new_dist += d3
                
                if j + 1 < len(best_path):
                    d4 = get_distance(distances, best_path[i + 1], best_path[j + 1])
                    if d4 is None:
                        continue
                    new_dist += d4
                
                # If improvement found, apply the swap
                if new_dist < current_dist:
                    # Reverse the segment between i+1 and j
                    best_path[i + 1:j + 1] = best_path[i + 1:j + 1][::-1]
                    improved = True
                    break
            
            if improved:
                break
    
    return best_path


def improve_with_3opt(
    distances: Dict[Tuple[str, str], int],
    path: List[str],
    max_iterations: int = 100
) -> List[str]:
    """
    3-opt improvement algorithm.
    
    More sophisticated than 2-opt, removes three edges and reconnects
    in a better way. Significantly slower but can find better solutions.
    
    Reference: https://en.wikipedia.org/wiki/Travelling_salesman_problem#k-opt_heuristic
    
    Args:
        distances: Distance dictionary
        path: Initial path
        max_iterations: Maximum number of iterations without improvement
    
    Returns:
        Improved path
    """
    improved = True
    iterations = 0
    best_path = path[:]
    n = len(best_path)
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(n - 2):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n):
                    # Try different reconnection possibilities
                    # This is a simplified 3-opt that checks a few reconnection cases
                    
                    # Calculate current distances
                    d_current = (
                        get_distance(distances, best_path[i], best_path[i + 1]) or 0 +
                        get_distance(distances, best_path[j], best_path[j + 1]) or 0 +
                        get_distance(distances, best_path[k], best_path[(k + 1) % n]) or 0
                    )
                    
                    # Try one reconnection: reverse segment between j+1 and k
                    new_path = (
                        best_path[:i + 1] +
                        best_path[j + 1:k + 1][::-1] +
                        best_path[i + 1:j + 1] +
                        best_path[k + 1:]
                    )
                    
                    d_new = (
                        get_distance(distances, new_path[i], new_path[i + 1]) or float('inf') +
                        get_distance(distances, new_path[j], new_path[j + 1]) or float('inf') +
                        get_distance(distances, new_path[k], new_path[(k + 1) % n]) or float('inf')
                    )
                    
                    if d_new < d_current:
                        best_path = new_path
                        improved = True
                        break
                
                if improved:
                    break
            
            if improved:
                break
    
    return best_path
