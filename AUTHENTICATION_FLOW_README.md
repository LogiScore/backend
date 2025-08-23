# LogiScore Authentication Flow Documentation

## Overview

The LogiScore backend now implements a proper separation between **sign-in** and **sign-up** authentication flows, addressing the security and user experience issues identified in the frontend implementation.

## Problem Statement

**Before**: The frontend was using a single `requestCode()` function for both sign-in and sign-up, which could:
- Send verification codes to non-existent users during sign-in attempts
- Create unnecessary user records during sign-in flows
- Mix sign-in and sign-up logic in a single endpoint

**After**: Separate, purpose-built endpoints that:
- Only send codes to existing users for sign-in
- Only send codes to new emails for sign-up
- Prevent duplicate user creation
- Maintain backward compatibility

## New Authentication Endpoints

### 1. Sign-In Flow (Existing Users)

#### Send Sign-In Code
```http
POST /api/auth/send-signin-code
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Behavior:**
- ✅ Only sends codes to **existing** users
- ✅ Updates existing user's verification code
- ✅ Returns success message (doesn't reveal user existence for security)
- ❌ Does NOT create new users

**Response:**
```json
{
  "message": "Verification code sent to your email",
  "expires_in": 10
}
```

#### Verify Sign-In Code
```http
POST /api/auth/verify-signin-code
Content-Type: application/json

{
  "email": "user@example.com",
  "code": "123456"
}
```

**Behavior:**
- ✅ Authenticates existing user
- ✅ Clears verification code after successful use
- ✅ Returns JWT access token and user data
- ❌ Does NOT modify user profile information

### 2. Sign-Up Flow (New Users)

#### Send Sign-Up Code
```http
POST /api/auth/send-signup-code
Content-Type: application/json

{
  "email": "newuser@example.com",
  "user_type": "shipper",
  "company_name": "New Company Ltd"
}
```

**Behavior:**
- ✅ Only sends codes to **new** email addresses
- ✅ Creates new user record with verification code
- ✅ Prevents duplicate sign-up attempts
- ❌ Does NOT send codes to existing users

**Response:**
```json
{
  "message": "Verification code sent to your email",
  "expires_in": 10
}
```

**Error Response (Existing User):**
```json
{
  "detail": "User with this email already exists. Please use sign-in instead."
}
```

#### Verify Sign-Up Code
```http
POST /api/auth/verify-signup-code
Content-Type: application/json

{
  "email": "newuser@example.com",
  "code": "123456",
  "full_name": "John Doe",
  "company_name": "New Company Ltd",
  "user_type": "shipper"
}
```

**Behavior:**
- ✅ Completes new user registration
- ✅ Updates user profile with provided information
- ✅ Marks user as verified
- ✅ Returns JWT access token and user data

## Security Features

### User Existence Privacy
- Sign-in endpoint doesn't reveal whether a user exists
- Both endpoints return the same success message for security
- Prevents email enumeration attacks

### Duplicate Prevention
- Sign-up endpoint explicitly checks for existing users
- Clear error message directing users to sign-in
- Prevents accidental duplicate account creation

### Code Expiration
- All verification codes expire after 10 minutes
- Codes are cleared after successful use
- Prevents code reuse attacks

## Backward Compatibility

The legacy endpoints are maintained for existing frontend implementations:

- `POST /api/auth/send-code` → Redirects to sign-up flow
- `POST /api/auth/verify-code` → Redirects to sign-up verification

**Note**: Legacy endpoints will be deprecated in future versions. Frontend should migrate to the new specific endpoints.

## Frontend Integration

### Recommended Implementation

```javascript
// For Sign-In (Existing Users)
async function requestSigninCode(email) {
  const result = await authMethods.requestSigninCode(email);
  // Only sends codes to existing users
}

async function signinWithCode(email, code) {
  const result = await authMethods.verifySigninCode(email, code);
  // Authenticates existing user
}

// For Sign-Up (New Users)
async function requestSignupCode(email, userType, companyName) {
  const result = await authMethods.requestSignupCode(email, userType, companyName);
  // Only sends codes to new emails
}

async function completeSignup(email, code, fullName, companyName, userType) {
  const result = await authMethods.verifySignupCode(email, code, fullName, companyName, userType);
  // Completes new user registration
}
```

### Error Handling

```javascript
try {
  const result = await authMethods.requestSignupCode(email, userType);
} catch (error) {
  if (error.response?.status === 400 && 
      error.response?.data?.detail?.includes("already exists")) {
    // User exists - redirect to sign-in
    showSigninForm();
  } else {
    // Handle other errors
    showErrorMessage(error.message);
  }
}
```

## Database Schema

The authentication system uses the existing `users` table with these key fields:

- `verification_code`: 6-digit verification code
- `verification_code_expires`: Expiration timestamp
- `is_verified`: Boolean flag for completed verification
- `user_type`: User role (shipper, forwarder, admin)
- `company_name`: Company name for business users

## Testing

Use the provided test script to verify endpoint functionality:

```bash
python test_auth_endpoints.py
```

The test script covers:
- ✅ Sign-up flow for new users
- ✅ Sign-in flow for existing users
- ✅ Duplicate sign-up prevention
- ✅ Legacy endpoint compatibility
- ✅ Security features (user existence privacy)

## Migration Guide

### For Frontend Developers

1. **Update API calls** to use specific endpoints:
   - Sign-in: `/api/auth/send-signin-code` and `/api/auth/verify-signin-code`
   - Sign-up: `/api/auth/send-signup-code` and `/api/auth/verify-signup-code`

2. **Implement proper error handling** for duplicate sign-up attempts

3. **Remove generic `requestCode()` function** and replace with specific functions

4. **Test both flows** to ensure proper separation

### For Backend Developers

1. **Monitor legacy endpoint usage** to plan deprecation
2. **Update API documentation** to reflect new endpoints
3. **Consider rate limiting** for verification code requests
4. **Monitor security logs** for potential abuse

## Future Enhancements

- [ ] Rate limiting for verification code requests
- [ ] SMS verification as alternative to email
- [ ] Two-factor authentication for admin users
- [ ] Audit logging for authentication attempts
- [ ] Account lockout after failed attempts

## Support

For questions or issues with the new authentication flow, please refer to:
- This documentation
- The test script for endpoint verification
- Backend logs for debugging
- API response codes and error messages
