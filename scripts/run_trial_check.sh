#!/bin/bash

# Trial Expiry Check Runner Script
# This script runs the trial expiry check with proper environment setup

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Set environment variables if not already set
export BACKEND_API_URL="${BACKEND_API_URL:-http://localhost:8000}"
export ADMIN_API_TOKEN="${ADMIN_API_TOKEN:-}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the trial expiry check
echo "Running trial expiry check..."
echo "Backend URL: $BACKEND_API_URL"
echo "Admin Token: ${ADMIN_API_TOKEN:+Set}${ADMIN_API_TOKEN:-Not set}"
echo ""

# Run with arguments passed to this script
python3 "$SCRIPT_DIR/check_trial_expiry.py" "$@"

echo ""
echo "Trial expiry check completed."
