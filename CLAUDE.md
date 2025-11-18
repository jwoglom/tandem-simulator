# Claude Code Development Guidelines

## Pre-Commit Checklist

**ALWAYS run `make lint` before committing any code changes.**

This ensures:
- ✅ Code is formatted with Black (line length 100)
- ✅ Imports are sorted correctly with isort
- ✅ No flake8 linting errors
- ✅ Type hints are validated with mypy

## Running Linting

```bash
make lint
```

If there are issues:
- **Black formatting**: Run `black tandem_simulator simulator.py tests/`
- **Import sorting**: Run `isort tandem_simulator simulator.py tests/`
- **Flake8 errors**: Fix manually (unused variables, etc.)
- **Mypy type errors**: Add type hints or assertions as needed

## Development Workflow

1. Make code changes
2. Run tests: `pytest` or `make test`
3. **Run linting: `make lint`** ← **CRITICAL STEP**
4. Fix any linting issues
5. Commit changes
6. Push to remote

## Why This Matters

The CI pipeline runs these same checks. If linting fails, the build fails. Running `make lint` locally before committing ensures:
- ✅ CI builds pass on first try
- ✅ Code quality remains high
- ✅ No formatting churn in pull requests
- ✅ Consistent code style across the project

## Other Useful Commands

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Format code (auto-fix)
make format

# Type check only
make type-check

# See all available commands
make help
```

## Notes

- Black and isort configuration is in `pyproject.toml`
- Mypy type checking is strict for core modules, relaxed for stubs
- Line length is set to 100 characters (not the default 88)
