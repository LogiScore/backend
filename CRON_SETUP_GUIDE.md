# Cron Job Setup Guide - Trial Reminder System

## 🎯 Overview

This guide helps you set up automated cron jobs for the LogiScore trial reminder system. The cron job will run daily to check for trials ending soon and send appropriate email notifications.

**Singapore Time (SGT)**: All times in this guide are in Singapore Standard Time (UTC+8).

### Timezone Reference
| Singapore Time | UTC Time | Cron Expression | Description |
|----------------|----------|-----------------|-------------|
| 9:00 AM SGT | 1:00 AM UTC | `0 1 * * *` | Business hours start |
| 12:00 PM SGT | 4:00 AM UTC | `0 4 * * *` | Lunch time |
| 5:00 PM SGT | 9:00 AM UTC | `0 9 * * *` | **Recommended** - End of business day |
| 9:00 PM SGT | 1:00 PM UTC | `0 13 * * *` | Evening check |

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
./scripts/setup_cron_job.sh
```

This script will:
- Check if a cron job already exists
- Add the trial check cron job
- Set up proper logging
- Provide next stepsdoes

### Option 2: Manual Setup

```bash
# 1. Open crontab editor
crontab -e

# 2. Add this line (runs daily at 5 PM Singapore Time)
0 9 * * * /path/to/LogiScore/backend/scripts/run_trial_check.sh >> /path/to/LogiScore/backend/logs/cron_trial_check.log 2>&1

# 3. Save and exit
```

## ⚙️ Configuration

### Environment Variables

Before setting up the cron job, ensure these environment variables are set:

```bash
# Required
export ADMIN_API_TOKEN="your-admin-token-here"
export BACKEND_API_URL="https://your-backend-url.com"

# Optional
export SENDGRID_API_KEY="your-sendgrid-key"
export SENDGRID_EU_RESIDENCY="false"
```

### Setting Environment Variables for Cron

Cron jobs run with minimal environment variables. You have several options:

#### Option 1: Add to crontab entry
```bash
# Add environment variables directly in crontab
0 9 * * * ADMIN_API_TOKEN="your-token" BACKEND_API_URL="https://your-url.com" /path/to/scripts/run_trial_check.sh >> /path/to/logs/cron_trial_check.log 2>&1
```

#### Option 2: Create environment file
```bash
# Create environment file
echo "ADMIN_API_TOKEN=your-admin-token-here" > /path/to/LogiScore/backend/.env.cron
echo "BACKEND_API_URL=https://your-backend-url.com" >> /path/to/LogiScore/backend/.env.cron

# Source in crontab
0 9 * * * . /path/to/LogiScore/backend/.env.cron && /path/to/scripts/run_trial_check.sh >> /path/to/logs/cron_trial_check.log 2>&1
```

#### Option 3: Add to system-wide environment
```bash
# Add to /etc/environment (system-wide)
sudo echo "ADMIN_API_TOKEN=your-admin-token-here" >> /etc/environment
sudo echo "BACKEND_API_URL=https://your-backend-url.com" >> /etc/environment
```

## 📅 Cron Schedule Options

### Daily at 5 PM Singapore Time (Recommended)
```bash
0 9 * * * /path/to/scripts/run_trial_check.sh
```
*Note: Cron uses UTC, so 9 AM UTC = 5 PM Singapore Time*

### Every 6 hours
```bash
0 */6 * * * /path/to/scripts/run_trial_check.sh
```

### Twice daily (5 PM and 2 AM Singapore Time)
```bash
0 9,18 * * * /path/to/scripts/run_trial_check.sh
```

### Weekdays only (Monday-Friday at 5 PM Singapore Time)
```bash
0 9 * * 1-5 /path/to/scripts/run_trial_check.sh
```

### Business hours (9 AM Singapore Time)
```bash
0 1 * * * /path/to/scripts/run_trial_check.sh
```
*Note: 1 AM UTC = 9 AM Singapore Time*

## 🧪 Testing

### Test the Script Manually
```bash
# Dry run (no emails sent)
./scripts/run_trial_check.sh --dry-run

# Test with real data
./scripts/run_trial_check.sh

# Test specific time window
./scripts/run_trial_check.sh --hours-ahead 12
```

### Test Cron Job
```bash
# Run cron job manually
sudo -u your-user /path/to/scripts/run_trial_check.sh --dry-run

# Check if cron service is running
sudo systemctl status cron
# or
sudo service cron status
```

## 📊 Monitoring

### Log Files
- **Cron output**: `logs/cron_trial_check.log`
- **Trial check logs**: `logs/trial_expiry_check.log`
- **System cron logs**: `/var/log/cron` or `/var/log/syslog`

### View Logs
```bash
# View recent cron output
tail -f logs/cron_trial_check.log

# View trial check logs
tail -f logs/trial_expiry_check.log

# View system cron logs
sudo tail -f /var/log/cron
```

### Check Cron Job Status
```bash
# List all cron jobs
crontab -l

# Check if cron service is running
sudo systemctl status cron

# View cron job history
grep "run_trial_check.sh" /var/log/cron
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Cron Job Not Running
```bash
# Check if cron service is running
sudo systemctl start cron
sudo systemctl enable cron

# Check cron logs
sudo tail -f /var/log/cron
```

#### 2. Permission Issues
```bash
# Make script executable
chmod +x scripts/run_trial_check.sh

# Check file permissions
ls -la scripts/run_trial_check.sh
```

#### 3. Environment Variables Not Set
```bash
# Test with explicit environment variables
ADMIN_API_TOKEN="your-token" BACKEND_API_URL="https://your-url.com" ./scripts/run_trial_check.sh --dry-run
```

#### 4. Path Issues
```bash
# Use absolute paths in crontab
/path/to/LogiScore/backend/scripts/run_trial_check.sh
```

### Debug Mode
```bash
# Run with verbose output
./scripts/run_trial_check.sh --dry-run --verbose

# Check script syntax
bash -n scripts/run_trial_check.sh
```

## 🛡️ Security Considerations

### 1. Secure Environment Variables
- Store sensitive tokens in secure files
- Use proper file permissions (600)
- Consider using a secrets management system

### 2. Log Rotation
```bash
# Set up log rotation for cron logs
sudo nano /etc/logrotate.d/logiscore-cron

# Add this content:
/path/to/LogiScore/backend/logs/cron_trial_check.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### 3. Monitoring and Alerts
- Set up monitoring for cron job failures
- Configure alerts for email sending failures
- Monitor trial conversion rates

## 📋 Production Checklist

- [ ] Environment variables configured
- [ ] Cron job added and tested
- [ ] Log files created and accessible
- [ ] Email service configured (SendGrid)
- [ ] Admin API token generated
- [ ] Backend API URL configured
- [ ] Dry-run test completed successfully
- [ ] Log rotation configured
- [ ] Monitoring set up
- [ ] Documentation updated

## 🆘 Support

If you encounter issues:

1. Check the logs in `logs/cron_trial_check.log`
2. Verify environment variables are set correctly
3. Test the script manually with `--dry-run`
4. Check system cron logs for errors
5. Contact the development team for assistance

## ✅ **Current Setup Summary**

Your trial reminder system is configured to run:
- **Time**: Daily at 5:00 PM Singapore Time (9:00 AM UTC)
- **Purpose**: Check for trials ending in the next 24 hours
- **Logs**: `logs/cron_trial_check.log`
- **Status**: ✅ Active and scheduled

### **Why 5 PM Singapore Time?**
- **End of business day**: Users are likely to check emails
- **Optimal timing**: Before evening activities begin
- **Global coverage**: Works well for Asia-Pacific region
- **Professional timing**: Avoids early morning or late night emails

---

**Cron job setup complete!** 🎉

Your trial reminder system will now run automatically and help improve trial conversion rates.
