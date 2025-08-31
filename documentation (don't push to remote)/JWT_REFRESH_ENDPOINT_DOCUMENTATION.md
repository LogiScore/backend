# JWT Refresh Endpoint Documentation

## Overview

The `/api/auth/refresh` endpoint allows clients to refresh expired JWT tokens without requiring users to re-authenticate. This provides a seamless user experience while maintaining security.

## Endpoint Details

- **URL**: `POST /api/auth/refresh`
- **Authentication**: None required (endpoint validates the expired token)
- **Content-Type**: `application/json`

## Request Format

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Request Parameters

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| `token`   | string | Yes      | The expired JWT token to refresh |

## Response Format

### Success Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Response Fields

| Field         | Type   | Description                                    |
|---------------|--------|------------------------------------------------|
| `access_token` | string | New valid JWT token                           |
| `token_type`   | string | Always "bearer"                               |
| `expires_in`   | number | Token expiration time in seconds (default: 1800) |

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid token format"
}
```
```json
{
  "detail": "Token missing user identifier"
}
```
```json
{
  "detail": "User not found"
}
```
```json
{
  "detail": "User account is inactive"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "token"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to refresh token"
}
```

## How It Works

1. **Token Validation**: The endpoint accepts an expired JWT token and validates its format and signature (ignoring expiration)
2. **User Verification**: Extracts the user ID from the token and verifies the user exists and is active
3. **New Token Generation**: Creates a new JWT token with the same user ID and current expiration time
4. **Response**: Returns the new token with metadata

## Security Features

- **Expired Token Handling**: Accepts expired tokens but validates their integrity
- **User Status Check**: Only refreshes tokens for active users
- **Token Validation**: Ensures token format and signature are valid
- **Comprehensive Logging**: Logs errors for debugging token-related issues

## Usage Examples

### Frontend Implementation

```javascript
// Example of using the refresh endpoint in a frontend application
async function refreshToken(expiredToken) {
  try {
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: expiredToken
      })
    });

    if (response.ok) {
      const data = await response.json();
      // Store the new token
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    } else {
      // Handle refresh failure (redirect to login)
      throw new Error('Token refresh failed');
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    // Redirect to login page
    window.location.href = '/login';
  }
}

// Usage in an interceptor or middleware
function setupTokenRefresh() {
  // Check if token is expired
  const token = localStorage.getItem('access_token');
  if (isTokenExpired(token)) {
    refreshToken(token)
      .then(newToken => {
        // Continue with the original request
      })
      .catch(() => {
        // Redirect to login
      });
  }
}
```

### Backend Integration

The refresh endpoint integrates seamlessly with existing authentication:

```python
# The endpoint automatically uses the same JWT configuration
# as other authentication endpoints
from auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Token expiration is configurable via environment variables
# Default: 30 minutes (1800 seconds)
```

## Configuration

The refresh endpoint uses the same JWT configuration as other authentication endpoints:

- **Secret Key**: `JWT_SECRET_KEY` environment variable
- **Algorithm**: HS256
- **Expiration**: `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutes)

## Error Handling

The endpoint provides comprehensive error handling:

1. **Invalid Token Format**: Returns 401 for malformed tokens
2. **Missing User ID**: Returns 401 if token payload is incomplete
3. **User Not Found**: Returns 401 if user no longer exists
4. **Inactive User**: Returns 401 if user account is deactivated
5. **Server Errors**: Returns 500 for unexpected errors with logging

## Logging

All token refresh attempts are logged for debugging:

- Successful refreshes are logged at INFO level
- Failed refreshes are logged at ERROR level with details
- Token validation errors are logged for security monitoring

## Backward Compatibility

This endpoint is fully backward compatible:

- No changes to existing authentication flow
- Existing tokens continue to work as before
- Frontend can optionally implement refresh logic
- Falls back to logout if refresh fails

## Testing

Use the provided test script to verify endpoint functionality:

```bash
python test_refresh_endpoint.py
```

The test script covers:
- Valid expired tokens
- Invalid token formats
- Missing parameters
- Non-existent users
- Error scenarios

## Best Practices

1. **Implement in Frontend**: Add token refresh logic to your frontend authentication flow
2. **Handle Failures Gracefully**: Redirect to login if refresh fails
3. **Monitor Usage**: Track refresh endpoint usage for security insights
4. **Rate Limiting**: Consider implementing rate limiting for production use
5. **Logging**: Monitor logs for unusual refresh patterns

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check token format and user existence
2. **500 Internal Server Error**: Check server logs for detailed error information
3. **Token Not Refreshing**: Verify user account is active and token is properly formatted

### Debug Steps

1. Check server logs for detailed error messages
2. Verify token format using JWT debugger
3. Confirm user exists and is active in database
4. Test with the provided test script

## Security Considerations

- **Token Reuse**: Old tokens remain valid until expiration
- **User Validation**: Only active users can refresh tokens
- **Audit Trail**: All refresh attempts are logged
- **Rate Limiting**: Consider implementing rate limiting for production

## Future Enhancements

Potential improvements for future versions:

1. **Refresh Token Rotation**: Implement refresh token rotation for enhanced security
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Audit Logging**: Enhanced logging for security monitoring
4. **Token Blacklisting**: Ability to blacklist compromised tokens

