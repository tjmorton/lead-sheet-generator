# Test Conventions — test-harness

## File layout

```
tests/
    __init__.py          # docstring: """Unit tests for the test_harness package."""
    test_<module>.py     # mirrors src/test_harness/<module>.py (flat / top-level only)
    <subpackage>/
        __init__.py      # docstring: """Tests for test_harness.<subpackage>."""
        test_<module>.py # mirrors src/test_harness/<subpackage>/<module>.py
```

Tests live under `tests/` alongside (not inside) `src/`.  The `[tool.pytest.ini_options]` block in `pyproject.toml` sets discovery to `testpaths = ["tests"]`.

Mirror the source subpackage structure under `tests/`. Each subdirectory needs its own `__init__.py` with a docstring describing what subpackage its tests cover.

| Source | Test file |
|--------|-----------|
| `src/test_harness/foo.py` | `tests/test_foo.py` |
| `src/test_harness/utils/bar.py` | `tests/utils/test_bar.py` |

## Naming

| Thing | Convention | Example |
|-------|-----------|---------|
| Test file | `test_<module>.py` | `test_messaging.py` for `messaging.py` |
| Test class | `Test<Concept>` | `TestPublishMessage`, `TestMain` |
| Test method | `test_<snake_case_behavior>` | `test_publishes_expected_message` |

Group related tests inside a class. Use standalone functions only when there is no natural grouping.

## Imports

```python
from test_harness import module_under_test
```

Always import the production module through the package. This ensures the installed package is tested, not a raw file path.

Use a module-level constant for long patch targets only when the same path is patched in multiple tests:

```python
_P = "test_harness.some_module"

@patch(f"{_P}.function_name")
def test_something(mock_fn): ...
```

## Testing modules with import-time side effects

Some modules run code at import time (e.g. `environment.py` calls `_load_environment()` at module level). This makes them unimportable when required env vars are missing.

To test such modules in isolation, use a helper that clears env vars, removes the cached module from `sys.modules`, and re-imports it with controlled env:

```python
import importlib
import sys

import pytest

MODULE = "test_harness.utils.environment"
_REQUIRED_ENV = {
    "RABBITMQ_HOST": "localhost",
    "RABBITMQ_PORT": "5672",
    "RABBITMQ_QUEUE_NAME": "test-queue",
    "RABBITMQ_USER": "guest",
    "RABBITMQ_PASSWORD": "guest",
}

@pytest.fixture(autouse=True)
def _reset_module():
    yield
    sys.modules.pop(MODULE, None)

def _import_module(monkeypatch, **overrides):
    for key in _REQUIRED_ENV:
        monkeypatch.delenv(key, raising=False)
    for key, value in {**_REQUIRED_ENV, **overrides}.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    sys.modules.pop(MODULE, None)
    return importlib.import_module(MODULE)
```

This is the **only** scenario where `@pytest.fixture(autouse=True)` is appropriate — the `autouse` fixture ensures `sys.modules` is cleaned up after every test so one test's import doesn't pollute the next.

## Assertions

| Use case | Style |
|----------|-------|
| Value equality | `assert result == expected` |
| Membership | `assert "needle" in haystack` |
| Exception expected | `with pytest.raises(ValueError, match="pattern"):` |
| Mock calls | `mock_fn.assert_called_once_with(arg)` / `mock_fn.assert_not_called()` |
| Captured output | `capsys.readouterr().out` then `assert` substrings |
| Floating point | `assert value == pytest.approx(3.14)` |

## Fixtures

- Prefer `capsys` for capturing `print()` output.
- Avoid `conftest.py` — place helpers directly in the test module as private functions (`_make_*`).
- The only `@pytest.fixture` with `autouse=True` is needed when tests must clean up `sys.modules` after themselves.

## Dev dependencies

- `pytest>=7.0.0` — test runner
- `pytest-cov>=4.0.0` — coverage (`uv run pytest --cov`)
- `pytest-dotenv>=0.5.0` — loads `.env` before tests (configured via `env_files = [".env"]` in `[tool.pytest.ini_options]`)
- `ruff>=0.8.0` — linter & formatter

## One assertion per test

Each test method should verify **one behaviour**.  If a test name needs "and" it probably should be two tests:

```python
# Good
def test_publishes_correct_message(self): ...
def test_handles_connection_failure(self): ...

# Avoid
def test_publishes_and_closes_connection(self): ...
```

## Running

All tests:
```bash
uv run pytest -v
```

A single file:
```bash
uv run pytest tests/utils/test_messaging.py -v
```

Coverage:
```bash
uv run pytest --cov=test_harness --cov-report=term-missing
```
