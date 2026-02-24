## 1. ACO implementation

- [x] 1.1 Implement `solve_tsp_aco(distances, points)` in `tsp_solver.py` with same signature and return type as existing solvers (permutation of points or None)
- [x] 1.2 Reuse existing helpers (`get_distance`, `calculate_path_distance`) for ACO; use fixed ACO parameters (ants, iterations, evaporation, alpha/beta) with sensible defaults
- [x] 1.3 Ensure ACO returns valid tour (all points exactly once, consecutive pairs in distance matrix) and handles empty/single-point inputs

## 2. Workflow and algorithm selection

- [x] 2.1 Add algorithm selection to main entry (e.g. `solve_tsp(..., algorithm=None)` or config); support `'aco'` and `'heuristic'`
- [x] 2.2 Default non–brute-force path (8–10 and >10 points) to ACO; keep brute force for ≤7 points unchanged
- [x] 2.3 When algorithm is `'heuristic'`, call existing heuristic path for 8–10 and >10 points; leave heuristic implementation in place and callable

## 3. Tests

- [x] 3.1 Add tests for `solve_tsp_aco`: valid tour shape, permutation, small instance correctness (e.g. fixed seed for reproducibility)
- [x] 3.2 Add tests for algorithm selection: default uses ACO for >7 points; explicit `heuristic` uses heuristic path; ≤7 points always use brute force
- [x] 3.3 Keep existing heuristic tests passing

## 4. Documentation

- [x] 4.1 Update README and/or ALGORITHMS.md: describe ACO, default (ACO) vs heuristic option, and how to switch back to heuristic if needed
