# Testing Guide

This project uses `pytest` for automated testing. The recommended workflow is:

1. Install dependencies with [uv](https://github.com/astral-sh/uv) if you have not already:  
   ```bash
   uv sync
   ```
2. Run the full test suite from the repository root:  
   ```bash
   uv run pytest
   ```

Additional notes:
- Snapshot and Textual-based tests require a terminal environment; `uv run pytest` handles the configured plugins.
- Coverage and parallel test helpers are included in the development dependencies (`pytest-cov`, `pytest-xdist`).
- When adding new tests, keep them under the `tests/` directory and name files `test_*.py`.
