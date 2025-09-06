#!/bin/bash

# Admin Daily Summary Script
# This script runs the admin daily summary and can be scheduled via cron

# Set the working directory to the project root
cd "$(dirname "$0")/.."

# Set environment variables if not already set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the daily summary script
python scripts/run_admin_daily_summary.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Admin daily summary completed successfully"
else
    echo "Admin daily summary failed"
    exit 1
fi
