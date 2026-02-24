# Spec: TSP ACO (Ant Colony Optimization)

## ADDED Requirements

### Requirement: ACO solver implements TSP contract

The system SHALL provide an Ant Colony Optimization (ACO) TSP solver that accepts the same inputs and returns the same output shape as the existing solvers: a distance matrix (dict mapping (from_id, to_id) to distance), a list of point IDs, and returns a permutation of point IDs as the tour, or None if no valid tour exists.

#### Scenario: ACO returns valid tour for non-empty points

- **WHEN** ACO solver is called with valid `distances` and a list of at least 2 `points`
- **THEN** it SHALL return a list of point IDs that is a permutation of `points` (each point exactly once) and forms a valid tour (every consecutive pair exists in `distances` or reverse)

#### Scenario: ACO handles empty or single point

- **WHEN** ACO solver is called with empty `points` or a single point
- **THEN** it SHALL return [] or the single-element list respectively, consistent with existing solver behavior

### Requirement: Default workflow uses ACO for non–brute-force sizes

The main TSP entry point (e.g. `solve_tsp`) SHALL use ACO as the default algorithm for problem sizes where the system does not use brute force (e.g. 8–10 and >10 points). Brute force SHALL remain used for very small instances (e.g. ≤7 points) with no change.

#### Scenario: Default algorithm for medium size is ACO

- **WHEN** the main solver is invoked with no algorithm override and more than 7 points
- **THEN** the system SHALL use the ACO implementation to produce the tour

#### Scenario: Very small size still uses brute force

- **WHEN** the main solver is invoked with 7 or fewer points
- **THEN** the system SHALL use brute force and SHALL NOT invoke ACO or heuristic for that call

### Requirement: Heuristic remains available and selectable

The existing heuristic implementation SHALL remain in the codebase and SHALL be callable when the user or configuration selects the heuristic algorithm. The system SHALL support an explicit choice (e.g. config or parameter) so the default can be ACO while allowing fallback to heuristic.

#### Scenario: Heuristic can be selected explicitly

- **WHEN** the user or configuration selects the heuristic algorithm (e.g. `algorithm='heuristic'`)
- **THEN** the system SHALL use the existing heuristic path for non–brute-force sizes and SHALL return a tour consistent with that implementation

#### Scenario: Heuristic code path is still tested

- **WHEN** tests run for the TSP solver
- **THEN** the heuristic algorithm SHALL remain covered by tests so that reverting the default to heuristic remains safe
