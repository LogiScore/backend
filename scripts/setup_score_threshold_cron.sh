#!/bin/bash

# Setup Score Threshold Cron Job
# This script adds the score threshold check to your cron jobs

echo "Setting up Score Threshold Cron Job..."
echo "====================================="

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCORE_SCRIPT="$PROJECT_DIR/scripts/run_score_threshold_check.sh"

echo "Project directory: $PROJECT_DIR"
echo "Score threshold script: $SCORE_SCRIPT"
echo ""

# Check if the script exists
if [ ! -f "$SCORE_SCRIPT" ]; then
    echo "❌ Error: Score threshold script not found at $SCORE_SCRIPT"
    exit 1
fi

# Make sure the script is executable
chmod +x "$SCORE_SCRIPT"
echo "✅ Made script executable"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"
echo "✅ Created logs directory"

# Remove any existing score threshold cron jobs
echo "Removing existing score threshold cron jobs..."
crontab -l 2>/dev/null | grep -v "run_score_threshold_check.sh" | crontab -

# Add the new cron job (run every hour)
CRON_ENTRY="0 * * * * $SCORE_SCRIPT >> $PROJECT_DIR/logs/cron_score_threshold.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Score threshold cron job added successfully!"
    echo ""
    echo "Cron job details:"
    echo "- Script: $SCORE_SCRIPT"
    echo "- Schedule: Every hour (0 * * * *)"
    echo "- Log file: $PROJECT_DIR/logs/cron_score_threshold.log"
    echo ""
    echo "Current cron jobs:"
    crontab -l
    echo ""
    echo "To test the script manually:"
    echo "  $SCORE_SCRIPT"
    echo ""
    echo "To monitor logs:"
    echo "  tail -f $PROJECT_DIR/logs/cron_score_threshold.log"
else
    echo "❌ Failed to add cron job!"
    exit 1
fi
