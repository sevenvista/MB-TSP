# Add Ant Colony Optimization (ACO) for TSP

## Why

The current TSP solver uses brute force (≤7 points) or heuristic algorithms (nearest neighbor + 2-opt/3-opt) for larger instances. The heuristic path can be too slow or suboptimal for some workloads. Adding Ant Colony Optimization (ACO) provides an alternative metaheuristic that may yield better quality or performance; we want it as the default in the workflow while retaining the existing heuristic implementation so we can experiment and switch back if ACO underperforms.

## What Changes

- Add an **Ant Colony Optimization (ACO)** implementation for TSP (same interface as existing solvers: `distances`, `points` → path).
- **Workflow**: Use ACO instead of the heuristic for the non–brute-force cases (e.g. small 8–10 and medium/large >10 points). Brute force for ≤7 points remains unchanged.
- **Retain** the current heuristic implementation in the codebase (no removal). It remains callable so we can compare results and revert the default to heuristic if ACO performance is not acceptable.
- Expose a way to choose the algorithm (e.g. config or parameter) so the default can be ACO with the option to use heuristic.
- Tests and documentation for ACO and the new default behavior.

## Capabilities

### New Capabilities

- `tsp-aco`: Ant Colony Optimization TSP solver and its use as the default non–brute-force algorithm in the solver workflow, with heuristic kept available as an alternative.

### Modified Capabilities

- *(None — no existing specs in `openspec/specs/`.)*

## Impact

- **Code**: `tsp_solver.py` (new ACO solver, `solve_tsp()` routing to ACO by default; heuristic path retained). Possible new module or section for ACO logic.
- **Configuration**: Any app or env configuration that selects TSP algorithm (if present) may need to support `aco` and `heuristic`; default set to ACO for the workflow.
- **Tests**: New tests for ACO and for algorithm selection (default = ACO, optional heuristic).
- **Docs**: README/ALGORITHMS (or equivalent) updated to describe ACO and the default vs heuristic option.
