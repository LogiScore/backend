#!/bin/bash

# Score Threshold Check Script
# This script runs the score threshold monitoring process

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Loaded environment variables from .env file"
else
    echo "Warning: .env file not found, using default values"
fi

# Environment variables are now loaded from .env file above

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the score threshold check
echo "Starting score threshold check at $(date)"
python3 scripts/check_score_thresholds.py

# Check exit status
if [ $? -eq 0 ]; then
    echo "Score threshold check completed successfully at $(date)"
else
    echo "Score threshold check failed at $(date)"
    exit 1
fi
