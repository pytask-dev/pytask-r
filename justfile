# Install all dependencies
install:
    uv sync --all-groups

# Run tests
test *FLAGS:
    uv run --group test pytest {{FLAGS}}

# Run tests with coverage
test-cov *FLAGS:
    uv run --group test pytest --cov=src --cov=tests --cov-report=xml -n auto {{FLAGS}}

# Run unit tests and doctests with coverage
test-unit:
    uv run --group test pytest -m "unit or (not integration and not end_to_end)" --cov=src --cov=tests --cov-report=xml -n auto

# Run end-to-end tests with coverage
test-e2e:
    uv run --group test pytest -m end_to_end --cov=src --cov=tests --cov-report=xml -n auto

# Run type checking
typing:
    uv run --group typing --group test ty check src/ tests/

# Run linting
lint:
    uvx prek run -a

# Run all checks (format, lint, typing, test)
check: lint typing test
