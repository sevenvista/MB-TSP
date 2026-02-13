import json
import os
from typing import List, Dict, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import Cell, EType, Distance
from astar import astar_pathfinding


class MapProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def normalize_grid(self, grid: List[List[Cell]]) -> List[List[Cell]]:
        """
        Normalize the grid by auto-generating IDs for cells without them.
        IDs are generated based on position: {type}_{row}_{col}
        """
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell.id is None:
                    # Auto-generate ID based on position
                    cell.id = f"{cell.type.value.lower()}_{row_idx}_{col_idx}"
        return grid
    
    def find_cells_by_type(
        self, 
        grid: List[List[Cell]], 
        cell_type: EType
    ) -> List[Tuple[Union[str, int], Tuple[int, int]]]:
        """Find all cells of a specific type and return (id, position)"""
        cells = []
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell.type == cell_type:
                    cells.append((cell.id, (row_idx, col_idx)))
        return cells
    
    def calculate_distance(
        self, 
        grid: List[List[Cell]], 
        from_id: Union[str, int], 
        from_pos: Tuple[int, int],
        to_id: Union[str, int],
        to_pos: Tuple[int, int]
    ) -> Distance:
        """Calculate distance between two points using A*"""
        distance = astar_pathfinding(grid, from_pos, to_pos)
        
        if distance is None:
            distance = -1  # Indicate no path exists
        
        return Distance(from_id=str(from_id), to_id=str(to_id), distance=distance)
    
    def process_map(self, grid: List[List[Cell]], mapid: Union[str, int]) -> List[Distance]:
        """
        Process the map and calculate all required distances using multithreading
        """
        # Normalize grid: auto-generate IDs for cells without them
        grid = self.normalize_grid(grid)
        
        # Find all relevant cells
        shelves = self.find_cells_by_type(grid, EType.SHELF)
        starts = self.find_cells_by_type(grid, EType.START)
        ends = self.find_cells_by_type(grid, EType.END)
        
        # Prepare all distance calculations
        tasks = []
        
        # SHELF to SHELF
        for i, (shelf1_id, shelf1_pos) in enumerate(shelves):
            for shelf2_id, shelf2_pos in shelves[i+1:]:
                tasks.append((shelf1_id, shelf1_pos, shelf2_id, shelf2_pos))
        
        # START to SHELF
        for start_id, start_pos in starts:
            for shelf_id, shelf_pos in shelves:
                tasks.append((start_id, start_pos, shelf_id, shelf_pos))
        
        # SHELF to END
        for shelf_id, shelf_pos in shelves:
            for end_id, end_pos in ends:
                tasks.append((shelf_id, shelf_pos, end_id, end_pos))
        
        # Execute calculations in parallel
        distances = []
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {
                executor.submit(
                    self.calculate_distance, 
                    grid, 
                    from_id, 
                    from_pos, 
                    to_id, 
                    to_pos
                ): (from_id, to_id)
                for from_id, from_pos, to_id, to_pos in tasks
            }
            
            for future in as_completed(futures):
                try:
                    distance = future.result()
                    distances.append(distance)
                except Exception as e:
                    from_id, to_id = futures[future]
                    print(f"Error calculating distance from {from_id} to {to_id}: {e}")
        
        # Save to file
        self.save_distances(mapid, distances)
        
        return distances
    
    def save_distances(self, mapid: Union[str, int], distances: List[Distance]):
        """Save distances to a JSON file"""
        filepath = os.path.join(self.data_dir, f"{mapid}.json")
        data = [d.model_dump() for d in distances]
        print(data)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_distances(self, mapid: Union[str, int]) -> Dict[Tuple[str, str], int]:
        """Load distances from a JSON file. IDs are always stored and returned as strings."""
        filepath = os.path.join(self.data_dir, f"{mapid}.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Map data not found for mapid: {mapid}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        distances = {}
        for item in data:
            key = (str(item['from_id']), str(item['to_id']))
            distances[key] = item['distance']
        
        return distances
