#!/bin/bash

# Subscription Expiration Check Script Wrapper
# This script ensures proper environment setup for the cronjob

# Set the working directory to the project root
# Try Render.com path first, fallback to current directory
if [ -d "/opt/render/project/src" ]; then
    cd /opt/render/project/src
    export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
else
    # For local development or other environments
    cd "$(dirname "$0")/.."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
fi

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Loaded environment variables from .env file"
else
    echo "Warning: .env file not found, using default values"
fi

# Run the subscription expiration check
python3 scripts/check_subscription_expiration.py

# Exit with the same code as the Python script
exit $?
