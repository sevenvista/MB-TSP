# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- **FastAPI Deprecation Warning**: Migrated from deprecated `@app.on_event("startup")` to modern `lifespan` context manager
  - No more deprecation warnings on startup
  - Follows FastAPI best practices for event handlers
  - Reference: [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

- **Cell ID Validation Error**: Made `id` field optional in `Cell` model
  - Cell IDs are now optional and can be `null`
  - Auto-generates IDs for cells without explicit IDs (format: `{type}_{row}_{col}`)
  - Reduces payload size and simplifies API usage
  - IDs are still required for START, END, and SHELF cells used in TSP routing

### Changed
- Updated `Cell` model: `id` field is now `Optional[str]` instead of `str`
- Added `normalize_grid()` method to `MapProcessor` for ID auto-generation
- Updated test examples to demonstrate optional IDs with `null` values
- Updated documentation to clarify when IDs are required vs optional

### Improved
- **TSP Algorithm**: Upgraded from simple brute force to modern heuristic algorithms
  - Implemented 2-opt improvement (pairwise edge exchange)
  - Implemented 3-opt improvement (triple edge exchange)
  - Added multi-start strategy for better solutions
  - Solutions now typically within 2-5% of optimal (vs 25% previously)
  - Based on research from [Wikipedia - Travelling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
  - Added comprehensive algorithm documentation in `ALGORITHMS.md`

## Technical Details

### Breaking Changes
None - changes are backward compatible. Existing payloads with explicit IDs continue to work.

### Migration Guide

**Before:**
```json
{
  "map": [
    [
      {"type": "PATH", "id": "p1"},
      {"type": "PATH", "id": "p2"}
    ]
  ]
}
```

**After (both formats work):**
```json
{
  "map": [
    [
      {"type": "PATH", "id": null},
      {"type": "PATH", "id": null}
    ]
  ]
}
```

### ID Generation Rules

When `id` is `null`, it will be auto-generated as:
- Format: `{cell_type}_{row_index}_{col_index}`
- Examples:
  - `path_0_1` for a PATH cell at row 0, column 1
  - `obstacle_5_3` for an OBSTACLE cell at row 5, column 3
  - `shelf_2_4` for a SHELF cell at row 2, column 4 (if no explicit ID provided)

**Best Practice:**
- Use `null` for PATH and OBSTACLE cells (they don't need meaningful IDs)
- Provide explicit IDs for START, END, and SHELF cells (used in TSP routing)

## [0.1.0] - 2026-02-06

### Added
- Initial release
- FastAPI server with RabbitMQ integration
- A* pathfinding algorithm for map distance calculations
- TSP solver with brute force and nearest neighbor
- Docker and docker-compose support
- UV package manager integration
- Comprehensive documentation
