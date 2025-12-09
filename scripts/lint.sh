#!/bin/bash
set -e

echo "Running flake8..."
flake8 app tests

echo "Running mypy..."
mypy app

echo "✓ Linting complete"
