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

# Run the subscription expiration check
python3 scripts/check_subscription_expiration.py

# Exit with the same code as the Python script
exit $?
