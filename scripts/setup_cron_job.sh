#!/bin/bash

# Cron Job Setup Script for Trial Reminder System
# This script helps set up the cron job for automated trial checking

echo "Setting up cron job for LogiScore Trial Reminder System..."
echo "=================================================="

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CRON_SCRIPT="$SCRIPT_DIR/run_trial_check.sh"

echo "Project directory: $PROJECT_DIR"
echo "Cron script: $CRON_SCRIPT"

# Check if the cron script exists and is executable
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "ERROR: Cron script not found at $CRON_SCRIPT"
    exit 1
fi

if [ ! -x "$CRON_SCRIPT" ]; then
    echo "Making cron script executable..."
    chmod +x "$CRON_SCRIPT"
fi

# Create the cron job entry (9 AM UTC = 5 PM Singapore Time)
CRON_ENTRY="0 9 * * * $CRON_SCRIPT >> $PROJECT_DIR/logs/cron_trial_check.log 2>&1"

echo ""
echo "Cron job entry to add:"
echo "$CRON_ENTRY"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_trial_check.sh"; then
    echo "WARNING: A trial check cron job already exists!"
    echo "Current cron jobs:"
    crontab -l | grep -E "(trial|logiscore)"
    echo ""
    read -p "Do you want to replace the existing cron job? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing trial check cron job..."
        crontab -l | grep -v "run_trial_check.sh" | crontab -
    else
        echo "Keeping existing cron job. Exiting."
        exit 0
    fi
fi

# Add the cron job
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Cron job details:"
    echo "- Runs daily at 5:00 PM Singapore Time (9:00 AM UTC)"
    echo "- Logs output to: $PROJECT_DIR/logs/cron_trial_check.log"
    echo "- Script location: $CRON_SCRIPT"
    echo ""
    echo "To view your current cron jobs:"
    echo "  crontab -l"
    echo ""
    echo "To remove this cron job:"
    echo "  crontab -e"
    echo "  (then delete the line with run_trial_check.sh)"
    echo ""
    echo "To test the cron job manually:"
    echo "  $CRON_SCRIPT --dry-run"
else
    echo "❌ Failed to add cron job!"
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Set up environment variables (ADMIN_API_TOKEN, BACKEND_API_URL)"
echo "2. Test the cron job with: $CRON_SCRIPT --dry-run"
echo "3. Monitor logs at: $PROJECT_DIR/logs/cron_trial_check.log"
echo ""
echo "Setup complete! 🎉"
