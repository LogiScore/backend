# LogiScore Subscription Expiration Management System

## Overview

The LogiScore backend now includes a comprehensive subscription expiration management system that automatically:

1. **Sends 7-day advance notifications** to users before their subscription expires
2. **Automatically reverts expired subscriptions** to the "Free" tier
3. **Tracks subscription status** with proper database fields
4. **Provides admin controls** for manual expiration management

## Database Schema Updates

### New User Table Fields

The following fields have been added to the `users` table:

```sql
-- Subscription management fields
subscription_start_date TIMESTAMP,           -- When subscription started
subscription_end_date TIMESTAMP,             -- When subscription expires
auto_renew_enabled BOOLEAN DEFAULT FALSE,    -- Whether auto-renewal is enabled
payment_method_id VARCHAR(255),              -- Stored payment method ID
stripe_subscription_id VARCHAR(255),         -- Stripe subscription ID
last_billing_date TIMESTAMP,                -- Last successful billing date
next_billing_date TIMESTAMP,                -- Next scheduled billing date
subscription_status VARCHAR(20) DEFAULT 'active'  -- active, past_due, canceled, expired, trial, expiring_soon
```

### Subscription Status Values

- `active` - Subscription is active and not expiring soon
- `expiring_soon` - Subscription expires within 7 days (notification sent)
- `expired` - Subscription has expired and been reverted to free
- `canceled` - Subscription was manually canceled
- `past_due` - Payment failed, subscription is past due
- `trial` - User is in trial period

## New Services

### 1. SubscriptionExpirationService

**Location**: `services/subscription_expiration_service.py`

**Key Methods**:
- `check_expiring_subscriptions()` - Main method to check and process expiring subscriptions
- `_send_expiration_notification()` - Sends 7-day warning emails
- `_revert_to_free_tier()` - Automatically reverts expired subscriptions
- `get_expiring_subscriptions_summary()` - Provides admin dashboard summary
- `force_check_expiration()` - Admin function to manually check a specific user

### 2. Enhanced EmailService

**New Email Templates**:
- **7-Day Warning**: `send_subscription_expiration_warning()`
- **Expiration Notification**: `send_subscription_expired_notification()`

## New Admin API Endpoints

### 1. Check All Expiring Subscriptions
```
POST /admin/subscriptions/check-expiration
```
Triggers a manual check for all expiring subscriptions and sends notifications.

### 2. Get Expiration Summary
```
GET /admin/subscriptions/expiration-summary
```
Returns summary statistics for admin dashboard:
```json
{
  "expiring_7_days": 5,
  "expiring_30_days": 12,
  "recently_expired": 3,
  "total_paid": 45,
  "checked_at": "2025-01-15T09:00:00"
}
```

### 3. Force Check Specific User
```
POST /admin/users/{user_id}/force-check-expiration
```
Manually checks expiration for a specific user (useful for testing or immediate processing).

## Automated Task

### Scheduled Script

**Location**: `scripts/check_subscription_expiration.py`

**Purpose**: Can be run as a cron job to automatically check for expiring subscriptions daily.

**Recommended Cron Schedule**:
```bash
# Check every day at 9:00 AM
0 9 * * * cd /path/to/logiscore/backend && python3 scripts/check_subscription_expiration.py
```

**Manual Execution**:
```bash
python3 scripts/check_subscription_expiration.py
```

## How It Works

### 1. Daily Check Process

1. **Query Database**: Find users with subscriptions expiring within 7 days
2. **Send Notifications**: Email users about upcoming expiration
3. **Update Status**: Mark users as `expiring_soon`
4. **Check Expired**: Find users whose subscriptions have already expired
5. **Revert to Free**: Automatically change expired subscriptions to free tier
6. **Send Notifications**: Email users about their expired subscription

### 2. Email Notifications

**7-Day Warning Email**:
- Personalized with user's name and subscription tier
- Shows exact expiration date and days remaining
- Explains what happens if not renewed
- Includes renewal link

**Expiration Notification Email**:
- Confirms subscription has expired
- Explains what free tier provides
- Includes renewal link
- Reassures that data is preserved

### 3. Automatic Tier Reversion

When a subscription expires:
- `subscription_tier` → `'free'`
- `subscription_status` → `'expired'`
- `subscription_end_date` → `NULL`
- `auto_renew_enabled` → `FALSE`

## Admin Dashboard Integration

### Subscription Status Overview

The admin dashboard now shows:
- **Expiring Soon**: Subscriptions expiring within 7 days
- **Expiring This Month**: Subscriptions expiring within 30 days
- **Recently Expired**: Subscriptions that expired in the last 7 days
- **Total Paid**: Current active paid subscriptions

### Manual Controls

Admins can:
- **Trigger Expiration Check**: Manually run the expiration check process
- **Force Check User**: Check a specific user's subscription status
- **View Summary**: See overview of subscription health

## Configuration

### Environment Variables

Ensure these are set for email functionality:
```bash
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@logiscore.com
FROM_NAME=LogiScore
```

### Database Migration

The subscription fields are already present in the database. If you need to add them manually:

```bash
python3 database/migrate_subscription_fields.py
```

## Testing

### Test Expiration Check

1. **Manual Check**:
   ```bash
   curl -X POST "https://logiscorebe.onrender.com/admin/subscriptions/check-expiration" \
        -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
   ```

2. **View Summary**:
   ```bash
   curl -X GET "https://logiscorebe.onrender.com/admin/subscriptions/expiration-summary" \
        -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
   ```

3. **Test Specific User**:
   ```bash
   curl -X POST "https://logiscorebe.onrender.com/admin/users/USER_ID/force-check-expiration" \
        -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
   ```

### Test Email Templates

The system includes fallback logging when SendGrid is not configured. Check the logs to see what emails would be sent.

## Monitoring and Logging

### Log Files

- **Main Application**: Standard application logs
- **Subscription Expiration**: `logs/subscription_expiration.log` (when running scheduled script)

### Key Log Messages

- `Found X users with expiring subscriptions`
- `Sending expiration notification to user X - Y days remaining`
- `Reverting user X from Y to free tier`
- `Subscription expiration check completed successfully`

## Troubleshooting

### Common Issues

1. **Emails Not Sending**: Check SendGrid API key and configuration
2. **Database Errors**: Verify subscription fields exist in users table
3. **Scheduled Task Fails**: Check script permissions and Python path

### Debug Mode

Enable detailed logging by setting log level to DEBUG in the script or application.

## Future Enhancements

### Planned Features

1. **Webhook Integration**: Real-time Stripe webhook processing
2. **Retry Logic**: Failed email notifications with retry mechanism
3. **Analytics**: Detailed subscription lifecycle analytics
4. **Custom Notification Schedules**: Configurable notification timing
5. **Bulk Operations**: Process multiple users simultaneously

### Integration Points

- **Stripe Webhooks**: Real-time subscription status updates
- **Admin Dashboard**: Enhanced subscription management interface
- **User Portal**: Subscription status and renewal options
- **Analytics**: Subscription lifecycle reporting

## Support

For questions or issues with the subscription expiration system:

1. Check the logs for detailed error messages
2. Verify database schema and field existence
3. Test email configuration with manual endpoint calls
4. Review cron job setup and permissions

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintainer**: LogiScore Development Team
