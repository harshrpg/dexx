#!/bin/bash

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test types
# pytest tests/unit -v
# pytest tests/integration -v
# pytest tests/e2e -v