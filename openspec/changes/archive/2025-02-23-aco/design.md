# Design: Ant Colony Optimization (ACO) for TSP

## Context

The TSP solver in `tsp_solver.py` currently branches by size: brute force for ≤7 points, nearest neighbor + 2-opt for 8–10, and a multi-start heuristic (NN + 2-opt + 3-opt) for >10 points. All solvers share the same interface: `(distances: Dict[(str,str), int], points: List[str]) -> Optional[List[str]]`. We want to add Ant Colony Optimization as an alternative metaheuristic, make it the default for the non–brute-force branches, and keep the existing heuristic implementation available so we can switch back without code removal. Constraints: same I/O contract, no new external dependencies unless justified, and algorithm choice must be configurable.

## Goals / Non-Goals

**Goals:**

- Implement ACO for TSP with the same function signature as existing solvers (`distances`, `points` → path).
- Use ACO by default for the workflow where heuristic is currently used (8–10 and >10 points); leave brute force (≤7) unchanged.
- Retain the full heuristic code path; expose a way to select algorithm (e.g. `aco` vs `heuristic`) so the default can be reverted to heuristic if needed.
- Add tests and documentation for ACO and algorithm selection.

**Non-Goals:**

- Changing brute force behavior or thresholds.
- Removing or rewriting the heuristic implementation.
- Adding a UI or API for algorithm selection (config/parameter only is in scope).

## Decisions

1. **Where to put ACO code**  
   Implement ACO in `tsp_solver.py` (e.g. `solve_tsp_aco(...)`) to keep all TSP strategies in one module and reuse `get_distance` / `calculate_path_distance`. Alternative: separate `tsp_aco.py`; rejected to avoid fragmentation and keep switching logic local.

2. **How to choose algorithm**  
   Use a single entry point that respects a choice (e.g. `solve_tsp(..., algorithm=None)` with `algorithm in ('aco', 'heuristic')` or env/config). Default = `'aco'` for non–brute-force; when `algorithm='heuristic'` or equivalent, call the existing heuristic path. This keeps rollout and rollback to heuristic trivial.

3. **ACO parameters**  
   Use fixed defaults (e.g. ant count, iterations, evaporation, alpha/beta) that work for typical instance sizes; no configuration surface for ACO parameters in this change. Tuning can be a follow-up.

4. **Size thresholds**  
   Keep current thresholds (≤7 brute force, 8–10 and >10). The same thresholds apply; only the implementation for 8–10 and >10 switches from heuristic to ACO by default. No new size-based branching.

## Risks / Trade-offs

- **ACO slower or worse quality than heuristic** → Mitigation: heuristic remains in code and selectable; default can be reverted to `heuristic` via config/parameter without redeploying code.
- **ACO non-determinism** → Mitigation: fix random seed in tests for reproducibility; document that ACO results may vary run-to-run.
- **Large instances** → ACO can be tuned (iterations, ants) later; initial implementation aims for correctness and parity with existing usage patterns.

## Migration Plan

1. Implement `solve_tsp_aco(distances, points)` and wire algorithm selection into `solve_tsp` (default `aco` for non–brute-force).
2. Add tests for ACO and for algorithm selection; ensure heuristic path still tested.
3. Update docs (README/ALGORITHMS).
4. Deploy with default ACO; if issues arise, change default (or config) to `heuristic` for rollback.

## Open Questions

- None for initial implementation. ACO parameter tuning (ants, iterations, evaporation) can be addressed in a later change if needed.
