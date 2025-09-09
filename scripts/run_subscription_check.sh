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

# Set environment variables for the script
export DATABASE_URL="sqlite:///./test.db"
export SENDGRID_API_KEY="your_sendgrid_api_key_here"
export MAIL_FROM="noreply@logiscore.com"
export MAIL_FROM_NAME="LogiScore"
export LOG_LEVEL="INFO"
export ENABLE_EMAIL_NOTIFICATIONS="True"
export ENABLE_SUBSCRIPTION_MANAGEMENT="True"

# Run the subscription expiration check
python3 scripts/check_subscription_expiration.py

# Exit with the same code as the Python script
exit $?
