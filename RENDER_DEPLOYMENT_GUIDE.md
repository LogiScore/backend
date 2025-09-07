# Trial Reminder System - Render Deployment Guide

## 🎯 Overview

This guide explains how to deploy the LogiScore trial reminder system on Render. The system automatically sends email notifications to users when their free trials are ending.

**Singapore Time (SGT)**: All times are in Singapore Standard Time (UTC+8).

## 🚀 Render Deployment Options

### Option 1: Background Worker (Recommended)

Render doesn't support traditional cron jobs, but you can use a Background Worker service:

#### 1. Create Background Worker Service

1. Go to your Render dashboard
2. Click "New +" → "Background Worker"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `logiscore-trial-reminder`
- **Environment**: `Python 3`
- **Region**: `Singapore (Asia Pacific)`
- **Branch**: `main`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python scripts/check_trial_expiry.py --hours-ahead 24`

#### 2. Configure Environment Variables

In the Render dashboard, go to Environment tab and add:

```
BACKEND_API_URL=https://your-backend-service.onrender.com
ADMIN_API_TOKEN=your-admin-token-here
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_EU_RESIDENCY=false
```

#### 3. Deploy

Click "Create Background Worker" to deploy.

### Option 2: External Cron Service

Use an external service to call your API endpoint:

#### 1. Set up External Cron Service

**Recommended Services:**
- **Cron-job.org** (free tier available)
- **EasyCron** 
- **SetCronJob**

#### 2. Configure Cron Job

- **URL**: `https://your-backend-service.onrender.com/api/notifications/check-trials`
- **Method**: `POST`
- **Schedule**: Daily at 5:00 PM Singapore Time (9:00 AM UTC)
- **Headers**: `Content-Type: application/json`

#### 3. Test the Endpoint

```bash
curl -X POST "https://your-backend-service.onrender.com/api/notifications/check-trials" \
  -H "Content-Type: application/json" \
  -d '{"hours_ahead": 24}'
```

### Option 3: Self-Hosted Server

If you have a separate server:

```bash
# Run the automated setup script
./scripts/setup_cron_job.sh
```

## ⚙️ Configuration

### Environment Variables

**Required:**
```
ADMIN_API_TOKEN=your-admin-token-here
BACKEND_API_URL=https://your-backend-service.onrender.com
```

**Optional:**
```
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_EU_RESIDENCY=false
```

### API Endpoints

The system provides these endpoints:

- `POST /api/notifications/check-trials` - External cron endpoint
- `POST /api/notifications/send-trial-warning` - Send trial warning
- `POST /api/notifications/send-trial-ended` - Send trial ended notification
- `GET /api/notifications/trials-ending-soon` - Get trials ending soon

## 📅 Scheduling Options

### Singapore Time Schedule

| Singapore Time | UTC Time | Cron Expression | Description |
|----------------|----------|-----------------|-------------|
| 9:00 AM SGT | 1:00 AM UTC | `0 1 * * *` | Business hours start |
| 12:00 PM SGT | 4:00 AM UTC | `0 4 * * *` | Lunch time |
| **5:00 PM SGT** | **9:00 AM UTC** | **`0 9 * * *`** | **✅ Recommended** |
| 9:00 PM SGT | 1:00 PM UTC | `0 13 * * *` | Evening check |

### Why 5 PM Singapore Time?

- **End of business day**: Users are likely to check emails
- **Optimal timing**: Before evening activities begin
- **Global coverage**: Works well for Asia-Pacific region
- **Professional timing**: Avoids early morning or late night emails

## 🧪 Testing

### Test API Endpoints

```bash
# Test external cron endpoint
curl -X POST "https://your-backend-service.onrender.com/api/notifications/check-trials" \
  -H "Content-Type: application/json" \
  -d '{"hours_ahead": 24}'

# Test trial warning
curl -X POST "https://your-backend-service.onrender.com/api/notifications/send-trial-warning" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "trial_duration": 7,
    "plan_name": "Subscription Monthly",
    "plan_price": 38,
    "billing_cycle": "month",
    "trial_end_date": "2024-01-15T23:59:59Z",
    "plan_features": ["Feature 1", "Feature 2"]
  }'
```

### Test Background Worker

1. Go to your Render dashboard
2. Click on your Background Worker service
3. Go to "Logs" tab
4. Check for successful execution

## 📊 Monitoring

### Render Dashboard

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor CPU and memory usage
- **Deployments**: Track deployment history

### API Response

The `/check-trials` endpoint returns:

```json
{
  "success": true,
  "message": "Trial check completed. Sent 5 warnings",
  "trials_checked": 8,
  "warnings_sent": 5,
  "timestamp": "2024-01-15T09:00:00Z"
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Background Worker Not Running
- Check environment variables are set correctly
- Verify the start command is correct
- Check logs for errors

#### 2. API Endpoint Not Working
- Verify the backend service is running
- Check if the endpoint is accessible
- Test with curl or Postman

#### 3. Email Not Sending
- Verify SendGrid API key is correct
- Check SendGrid dashboard for delivery status
- Review logs for email errors

### Debug Steps

1. **Check Logs**: View logs in Render dashboard
2. **Test Endpoints**: Use curl to test API endpoints
3. **Verify Environment**: Ensure all environment variables are set
4. **Check Database**: Verify trial data exists in database

## 🛡️ Security

### API Security
- Use HTTPS for all API calls
- Implement proper authentication
- Rate limit API endpoints

### Environment Variables
- Store sensitive tokens securely
- Use Render's environment variable system
- Never commit secrets to code

## 📋 Production Checklist

- [ ] Background Worker service created
- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] Email service configured (SendGrid)
- [ ] Schedule configured (5 PM SGT)
- [ ] Monitoring set up
- [ ] Logs accessible
- [ ] Error handling tested

## 🆘 Support

If you encounter issues:

1. Check the logs in Render dashboard
2. Verify environment variables are set correctly
3. Test API endpoints manually
4. Check SendGrid dashboard for email delivery
5. Contact the development team for assistance

---

**Deployment complete!** 🎉

Your trial reminder system will now run automatically on Render and help improve trial conversion rates.
