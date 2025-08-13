#!/bin/bash

# Navigate to your project directory (update this if needed)
cd "$(dirname "$0")"

# Activate poetry environment
source "$(poetry env info --path)/bin/activate"

# Check for --no-reload or -nr flag
if [[ "$*" == *"--no-reload"* ]] || [[ "$*" == *"-nr"* ]]; then
    # Run without reload
    poetry run uvicorn app.main:app --workers 8 --loop uvloop --http h11
else
    # Run with reload
    poetry run uvicorn app.main:app --reload
fi