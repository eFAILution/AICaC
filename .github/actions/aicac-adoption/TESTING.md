# Testing Guide

Run tests for the AICaC adoption action.

## Quick Start

```bash
# Install dependencies
pip install pytest pytest-cov pyyaml

# Run all tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html
```

## Test Files

- `test_bootstrap.py` - Bootstrap functionality
- `test_validate.py` - Validation logic
- `test_update_badge.py` - Badge updates
- `conftest.py` - Shared fixtures

## Coverage Target

80% minimum coverage configured in `pytest.ini`
