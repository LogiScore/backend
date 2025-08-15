# SendGrid Integration Setup

This guide explains how to set up SendGrid email integration for the LogiScore backend.

## Prerequisites

1. A SendGrid account (free tier available)
2. A verified sender domain or email address
3. API key with appropriate permissions

## Setup Steps

### 1. Create SendGrid Account

1. Go to [SendGrid.com](https://sendgrid.com) and create an account
2. Verify your email address
3. Complete account verification

### 2. Verify Sender Identity

#### Option A: Verify a Single Sender (Recommended for testing)
1. In SendGrid dashboard, go to **Settings > Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in the form with your details:
   - From Name: LogiScore
   - From Email: noreply@logiscore.com (or your verified email)
   - Company: Your company name
   - Address: Your business address
4. Click **Create**
5. Check your email and click the verification link

#### Option B: Verify a Domain (Recommended for production)
1. In SendGrid dashboard, go to **Settings > Sender Authentication**
2. Click **Authenticate Your Domain**
3. Follow the DNS setup instructions
4. Wait for DNS propagation (can take up to 48 hours)

### 3. Create API Key

1. In SendGrid dashboard, go to **Settings > API Keys**
2. Click **Create API Key**
3. Choose **Full Access** or **Restricted Access** with these permissions:
   - Mail Send: Full Access
   - Mail Settings: Read Access
4. Click **Create & View**
5. Copy the API key (you won't see it again)

### 4. Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and set your SendGrid configuration:
   ```bash
   SENDGRID_API_KEY=your_actual_api_key_here
   FROM_EMAIL=noreply@logiscore.com
   FROM_NAME=LogiScore
   SENDGRID_EU_RESIDENCY=false
   ```

### 5. Test the Integration

1. Start your backend server
2. Use the `/api/users/request-code` endpoint to test email sending
3. Check the console logs for any errors
4. Verify that emails are received

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | Your SendGrid API key | `SG.abc123...` |
| `FROM_EMAIL` | Sender email address | `noreply@logiscore.com` |
| `FROM_NAME` | Sender display name | `LogiScore` |
| `SENDGRID_EU_RESIDENCY` | Enable EU data residency | `false` |

## Fallback Mode

If SendGrid is not configured or fails:
- Verification codes are logged to the console
- The system continues to work for development/testing
- No emails are sent, but authentication still works

## Troubleshooting

### Common Issues

1. **"Invalid API Key" error**
   - Verify your API key is correct
   - Check if the key has the right permissions

2. **"Sender not verified" error**
   - Complete sender verification in SendGrid
   - Wait for DNS propagation if using domain verification

3. **Emails not received**
   - Check spam/junk folders
   - Verify sender email is correct
   - Check SendGrid activity logs

4. **Rate limiting**
   - Free tier: 100 emails/day
   - Paid tiers: Higher limits
   - Check your SendGrid dashboard for usage

### Debug Mode

Enable debug logging by setting the log level in your environment:
```bash
LOG_LEVEL=DEBUG
```

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secure secret management
   - Rotate keys regularly

2. **Email Security**
   - Use SPF, DKIM, and DMARC records
   - Monitor for abuse and phishing attempts
   - Implement rate limiting

3. **Data Privacy**
   - Consider GDPR compliance if serving EU users
   - Enable EU data residency if needed
   - Implement proper data retention policies

## Production Deployment

1. **Environment Variables**
   - Set all required environment variables in your deployment platform
   - Use secure secret management (e.g., Render secrets, Vercel environment variables)

2. **Monitoring**
   - Set up SendGrid webhooks for delivery tracking
   - Monitor email delivery rates and bounces
   - Set up alerts for failures

3. **Scaling**
   - Monitor SendGrid usage and limits
   - Consider upgrading to paid tiers for higher limits
   - Implement email queuing for high-volume scenarios
