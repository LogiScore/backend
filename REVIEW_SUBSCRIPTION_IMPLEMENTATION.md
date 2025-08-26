# Review Subscription System Implementation

## Overview

The LogiScore backend now includes a comprehensive review subscription system that allows users to:
- Subscribe to reviews based on specific criteria (freight forwarder, location, review type)
- Receive real-time notifications when new reviews match their preferences
- Choose notification frequency (immediate, daily, or weekly)
- Manage their subscription preferences through a RESTful API

## New Database Tables

### 1. `review_subscriptions`
Stores user subscription preferences and criteria.

**Fields:**
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users table)
- `freight_forwarder_id` (UUID, Optional - specific forwarder)
- `location_country` (VARCHAR(100), Optional - country filter)
- `location_city` (VARCHAR(100), Optional - city filter)
- `review_type` (VARCHAR(50), Optional - review type filter)
- `notification_frequency` (VARCHAR(20), Default: 'immediate')
- `is_active` (BOOLEAN, Default: TRUE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

### 2. `review_notifications`
Tracks notification delivery status.

**Fields:**
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users table)
- `review_id` (UUID, Foreign Key to reviews table)
- `subscription_id` (UUID, Foreign Key to review_subscriptions table)
- `notification_type` (VARCHAR(50), Default: 'new_review')
- `is_sent` (BOOLEAN, Default: FALSE)
- `sent_at` (TIMESTAMP WITH TIME ZONE)
- `created_at` (TIMESTAMP WITH TIME ZONE)

## API Endpoints

### Review Subscriptions (`/api/review-subscriptions`)

#### Create Subscription
```http
POST /api/review-subscriptions/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "freight_forwarder_id": "uuid-optional",
  "location_country": "string-optional",
  "location_city": "string-optional",
  "review_type": "string-optional",
  "notification_frequency": "immediate|daily|weekly"
}
```

#### Get User Subscriptions
```http
GET /api/review-subscriptions/
Authorization: Bearer <jwt_token>
```

#### Get Specific Subscription
```http
GET /api/review-subscriptions/{subscription_id}
Authorization: Bearer <jwt_token>
```

#### Update Subscription
```http
PUT /api/review-subscriptions/{subscription_id}
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "location_country": "new-country",
  "notification_frequency": "daily"
}
```

#### Delete Subscription
```http
DELETE /api/review-subscriptions/{subscription_id}
Authorization: Bearer <jwt_token>
```

#### Toggle Subscription Status
```http
POST /api/review-subscriptions/{subscription_id}/toggle
Authorization: Bearer <jwt_token>
```

## Email Notifications

### 1. Immediate Notifications
Sent instantly when a new review matches subscription criteria.

**Features:**
- Personalized greeting with user's name
- Review details (forwarder name, rating, location, type)
- Direct link to view the full review
- Unsubscribe and subscription management links

### 2. Daily/Weekly Summaries
Aggregated notifications sent at specified intervals.

**Features:**
- Summary statistics (total new reviews)
- List of recent reviews with key details
- Links to view all reviews
- Subscription management options

## Notification Service

The `NotificationService` class handles:
- Processing new reviews for matching subscriptions
- Sending immediate notifications
- Generating and sending summary emails
- Cleaning up old notification records

### Key Methods:
- `process_new_review()` - Process new review and send notifications
- `send_daily_summaries()` - Send daily summary emails
- `send_weekly_summaries()` - Send weekly summary emails
- `cleanup_old_notifications()` - Clean up old records

## Webhook Integration

The system integrates with existing webhooks to automatically trigger notifications:

### Review Events:
- `review.created` - Triggers immediate notifications
- `review.updated` - Triggers notifications for updates

### Stripe Events:
- Existing payment and subscription webhooks remain unchanged

## Database Migration

### Running the Migration
```bash
cd database
python migrate_review_subscriptions.py
```

### What the Migration Does:
1. Creates `review_subscriptions` table
2. Creates `review_notifications` table
3. Adds appropriate indexes for performance
4. Sets up foreign key constraints
5. Verifies the migration was successful

## Configuration

### Environment Variables
The system uses existing environment variables:
- `SENDGRID_API_KEY` - For sending emails
- `FROM_EMAIL` - Sender email (noreply@logiscore.net)
- `FROM_NAME` - Sender name (LogiScore)

### Email Templates
All email templates are HTML-based with:
- Responsive design
- Professional styling
- Clear call-to-action buttons
- Unsubscribe links for compliance

## Security Features

- JWT authentication required for all subscription endpoints
- Users can only access their own subscriptions
- Input validation and sanitization
- Rate limiting through existing FastAPI middleware

## Performance Considerations

- Database indexes on frequently queried fields
- Efficient subscription matching algorithms
- Asynchronous email sending
- Batch processing for summary emails

## Monitoring and Logging

- Comprehensive logging for all operations
- Error tracking and reporting
- Success/failure metrics for notifications
- Database query performance monitoring

## Future Enhancements

### Planned Features:
1. **Push Notifications** - Mobile app integration
2. **SMS Notifications** - Text message alerts
3. **Advanced Filtering** - Rating ranges, date ranges
4. **Bulk Operations** - Manage multiple subscriptions
5. **Analytics Dashboard** - Subscription insights

### Scalability Improvements:
1. **Queue System** - Redis/RabbitMQ for notifications
2. **Background Workers** - Celery for async processing
3. **Caching Layer** - Redis for subscription data
4. **Database Sharding** - For high-volume scenarios

## Testing

### Manual Testing
1. Create a review subscription
2. Submit a new review matching the criteria
3. Verify email notification is received
4. Test different notification frequencies

### Automated Testing
```bash
# Run the test suite
pytest tests/test_review_subscriptions.py

# Test notification service
pytest tests/test_notification_service.py
```

## Deployment

### Prerequisites
1. Database migration completed
2. SendGrid API key configured
3. Environment variables set
4. Webhook endpoints accessible

### Deployment Steps
1. Run database migration
2. Deploy updated backend code
3. Test webhook endpoints
4. Monitor email delivery
5. Verify subscription creation

## Support and Troubleshooting

### Common Issues:
1. **Emails not sending** - Check SendGrid API key and configuration
2. **Subscriptions not matching** - Verify review data format
3. **Database errors** - Check migration status and constraints
4. **Webhook failures** - Verify endpoint accessibility and authentication

### Debug Mode:
Enable detailed logging by setting log level to DEBUG in the configuration.

## API Documentation

Full API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Contributing

When adding new features to the subscription system:
1. Update this documentation
2. Add appropriate tests
3. Follow existing code patterns
4. Update API documentation
5. Consider backward compatibility

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Maintainer:** Backend Team
