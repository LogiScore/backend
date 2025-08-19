# LogiScore Contact Form API Documentation

## Overview
The LogiScore Contact Form API provides a robust endpoint for handling contact form submissions with intelligent email routing and automatic acknowledgment sending. This API is designed to streamline customer communication by automatically directing inquiries to the appropriate team members.

## Endpoint Details

**URL:** `POST /api/email/contact-form`  
**Base URL:** `https://your-logiscore-backend.onrender.com`  
**Full Endpoint:** `https://your-logiscore-backend.onrender.com/api/email/contact-form`

## Request Payload

### JSON Structure
```json
{
  "name": "string",
  "email": "string", 
  "contact_reason": "string",
  "subject": "string",
  "message": "string"
}
```

### Field Specifications

| Field | Type | Required | Validation Rules | Description |
|-------|------|----------|------------------|-------------|
| `name` | string | ✅ | 2-100 characters | User's full name |
| `email` | string | ✅ | Valid email format | User's email address for acknowledgment |
| `contact_reason` | string | ✅ | One of predefined values | Reason for contact (see routing table below) |
| `subject` | string | ✅ | 5-200 characters | Email subject line |
| `message` | string | ✅ | 10-2000 characters | User's message content |

### Contact Reason Values
The `contact_reason` field determines which team receives the inquiry:

| Contact Reason | Route To | Email Address | Description |
|----------------|----------|---------------|-------------|
| `feedback` | Feedback Team | feedback@logiscore.net | Platform feedback and suggestions |
| `support` | Technical Support | support@logiscore.net | Technical issues and assistance |
| `billing` | Accounts/Billing | accounts@logiscore.net | Payment and subscription inquiries |
| `reviews` | Review Disputes | dispute@logiscore.net | Review-related issues and disputes |
| `privacy` | Data Protection Officer | dpo@logiscore.net | Privacy and data protection concerns |
| `general` | General Inquiries | support@logiscore.net | General questions and inquiries |

## Response Format

### Success Response (200 OK)
```json
{
  "message": "Contact form submitted successfully",
  "email_sent": true,
  "acknowledgment_sent": true,
  "routed_to": "support@logiscore.net"
}
```

### Error Responses

#### Validation Error (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "detail": "Failed to process contact form. Please try again later."
}
```

## Email Templates

### 1. Team Notification Email
- **From:** noreply@logiscore.com (or configured sender)
- **To:** Appropriate team email based on contact_reason
- **Subject:** `[Contact Form] {original_subject}`
- **Content:** Professional format with all form data, timestamp, and routing information

### 2. User Acknowledgment Email
- **From:** noreply@logiscore.com (or configured sender)
- **To:** User's email address from the form
- **Subject:** "Thank you for contacting LogiScore"
- **Content:** Confirmation of receipt, next steps, and professional acknowledgment

## Security Features

### Input Validation
- **Name:** 2-100 characters, stripped of leading/trailing whitespace
- **Email:** Valid email format using Pydantic EmailStr
- **Contact Reason:** Strict validation against predefined values
- **Subject:** 5-200 characters, stripped of whitespace
- **Message:** 10-2000 characters with XSS protection

### XSS Protection
- Automatic removal of `<script>` tags from message content
- HTML content sanitization before email generation

### Rate Limiting Considerations
- Implement rate limiting at the application level if needed
- Consider IP-based or user-based throttling for production use

## Implementation Example

### Frontend (JavaScript)
```javascript
const submitContactForm = async (formData) => {
  try {
    const response = await fetch('/api/email/contact-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: formData.name,
        email: formData.email,
        contact_reason: formData.contact_reason,
        subject: formData.subject,
        message: formData.message
      })
    });

    if (response.ok) {
      const result = await response.json();
      console.log('Contact form submitted:', result);
      // Handle success
    } else {
      const error = await response.json();
      console.error('Contact form error:', error);
      // Handle error
    }
  } catch (error) {
    console.error('Network error:', error);
    // Handle network error
  }
};
```

### Frontend (SvelteKit)
```svelte
<script>
  import { onMount } from 'svelte';
  
  let formData = {
    name: '',
    email: '',
    contact_reason: 'general',
    subject: '',
    message: ''
  };
  
  let submitting = false;
  let message = '';
  
  const contactReasons = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'support', label: 'Technical Support' },
    { value: 'feedback', label: 'Feedback' },
    { value: 'billing', label: 'Billing' },
    { value: 'reviews', label: 'Reviews' },
    { value: 'privacy', label: 'Privacy' }
  ];
  
  async function handleSubmit() {
    submitting = true;
    message = '';
    
    try {
      const response = await fetch('/api/email/contact-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        message = 'Thank you! Your message has been sent successfully.';
        formData = { name: '', email: '', contact_reason: 'general', subject: '', message: '' };
      } else {
        message = `Error: ${result.detail}`;
      }
    } catch (error) {
      message = 'Network error. Please try again.';
    } finally {
      submitting = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label for="name">Name *</label>
    <input 
      id="name" 
      type="text" 
      bind:value={formData.name} 
      required 
      minlength="2" 
      maxlength="100"
    />
  </div>
  
  <div>
    <label for="email">Email *</label>
    <input 
      id="email" 
      type="email" 
      bind:value={formData.email} 
      required
    />
  </div>
  
  <div>
    <label for="contact_reason">Contact Reason *</label>
    <select id="contact_reason" bind:value={formData.contact_reason} required>
      {#each contactReasons as reason}
        <option value={reason.value}>{reason.label}</option>
      {/each}
    </select>
  </div>
  
  <div>
    <label for="subject">Subject *</label>
    <input 
      id="subject" 
      type="text" 
      bind:value={formData.subject} 
      required 
      minlength="5" 
      maxlength="200"
    />
  </div>
  
  <div>
    <label for="message">Message *</label>
    <textarea 
      id="message" 
      bind:value={formData.message} 
      required 
      minlength="10" 
      maxlength="2000"
      rows="5"
    ></textarea>
  </div>
  
  <button type="submit" disabled={submitting}>
    {submitting ? 'Sending...' : 'Send Message'}
  </button>
  
  {#if message}
    <div class="message">{message}</div>
  {/if}
</form>
```

## Testing

### Test Script
Run the included test script to verify functionality:
```bash
python test_contact_form.py
```

### Manual Testing
Test the endpoint with different contact reasons:
```bash
curl -X POST "https://your-backend.onrender.com/api/email/contact-form" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "contact_reason": "support",
    "subject": "Test Contact Form",
    "message": "This is a test message to verify the contact form functionality."
  }'
```

## Environment Variables

Ensure these environment variables are set in your backend:
```bash
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@logiscore.com
FROM_NAME=LogiScore
SENDGRID_EU_RESIDENCY=false  # Set to true for EU data residency
```

## Monitoring and Logging

The API includes comprehensive logging:
- Contact form submissions with user email and reason
- Email routing decisions
- Email sending success/failure status
- Error details for debugging

Check your backend logs for detailed information about contact form processing.

## Error Handling

### Common Issues
1. **SendGrid API errors:** Check API key and SendGrid account status
2. **Invalid email addresses:** Ensure proper email format validation
3. **Rate limiting:** Monitor for potential spam submissions
4. **Template rendering errors:** Check for malformed HTML in email templates

### Fallback Mode
When SendGrid is unavailable, the system logs emails to console for development purposes and returns success status.

## Future Enhancements

Consider implementing these features for production use:
- Database storage of contact form submissions
- Advanced spam detection and filtering
- Email template customization via admin panel
- Contact form analytics and reporting
- Integration with customer support systems (Zendesk, Intercom, etc.)

## Support

For technical support with this API endpoint, contact the development team or refer to the backend logs for detailed error information.
