# Review Thank You Email Endpoint

## Overview
The `/api/email/review-thank-you` endpoint sends personalized thank you emails to users after they submit a review. The email includes a summary of their review with the freight forwarder name, location, and individual category ratings.

## Endpoint Details

**URL:** `POST /api/email/review-thank-you`  
**Base Path:** `/api/email`  
**Tags:** `email`

## Request Format

### JSON Payload
```json
{
    "review_id": "uuid-string"
}
```

### Parameters
- `review_id` (required): The UUID of the submitted review

## Response Format

### Success Response (200)
```json
{
    "success": true,
    "message": "Thank you email sent successfully",
    "email_sent_to": "user@example.com"
}
```

### Error Responses

#### 400 Bad Request
```json
{
    "detail": "review_id is required"
}
```
```json
{
    "detail": "Cannot send email for anonymous reviews or users without email"
}
```

#### 404 Not Found
```json
{
    "detail": "Review not found"
}
```
```json
{
    "detail": "Freight forwarder not found"
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Failed to send thank you email"
}
```
```json
{
    "detail": "Internal server error while sending thank you email"
}
```

## Email Content

The thank you email includes:

1. **Personalized greeting** with the user's name
2. **Review summary** showing:
   - Freight forwarder name
   - Location (city, country)
3. **Detailed ratings table** with:
   - Category names
   - Question text
   - Star ratings (⭐)
   - Rating definitions
4. **Call-to-action** button linking to LogiScore
5. **Professional styling** with LogiScore branding

## Email Template Features

- **Responsive design** for mobile and desktop
- **Professional styling** with LogiScore color scheme
- **Clear information hierarchy** for easy reading
- **Accessible design** with proper contrast and structure
- **Fallback handling** when SendGrid is unavailable

## Implementation Details

### Database Queries
The endpoint performs the following database operations:
1. Retrieves the review by ID
2. Fetches the freight forwarder information
3. Gets user details (if not anonymous)
4. Retrieves all category scores for the review

### Email Service Integration
- Uses the existing `EmailService` class
- Integrates with SendGrid for email delivery
- Includes fallback logging for development environments
- Supports EU data residency configuration

### Security Considerations
- Only sends emails to authenticated users (not anonymous reviews)
- Validates review ownership and existence
- Logs all email operations for audit purposes

## Usage Examples

### Frontend Integration
```javascript
// After successful review submission
const response = await fetch('/api/email/review-thank-you', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        review_id: submittedReviewId
    })
});

if (response.ok) {
    const result = await response.json();
    console.log('Thank you email sent to:', result.email_sent_to);
}
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/email/review-thank-you" \
     -H "Content-Type: application/json" \
     -d '{"review_id": "your-review-uuid-here"}'
```

## Testing

A test script `test_review_thank_you_email.py` is provided to verify the endpoint functionality:

```bash
python test_review_thank_you_email.py
```

**Note:** Update the `review_id` in the test script with an actual review ID from your database.

## Dependencies

- FastAPI
- SQLAlchemy
- SendGrid Python library
- Existing LogiScore database models and email service

## Environment Variables

The endpoint uses the same environment variables as the existing email service:
- `SENDGRID_API_KEY`: SendGrid API key for email delivery
- `FROM_EMAIL`: Sender email address
- `FROM_NAME`: Sender name
- `SENDGRID_EU_RESIDENCY`: EU data residency setting (optional)

## Error Handling

The endpoint includes comprehensive error handling:
- Input validation
- Database error handling
- Email service error handling
- Proper HTTP status codes
- Detailed error messages for debugging

## Logging

All operations are logged for monitoring and debugging:
- Successful email sends
- Failed email attempts
- Database query errors
- General exceptions

## Future Enhancements

Potential improvements for future versions:
- Email templates customization
- Multiple language support
- Email delivery tracking
- Retry mechanisms for failed sends
- Rate limiting for email sending
