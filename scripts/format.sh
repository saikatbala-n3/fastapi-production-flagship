#!/bin/bash
set -e

echo "Running black..."
black app tests

echo "Running isort..."
isort app tests

echo "✓ Formatting complete"
