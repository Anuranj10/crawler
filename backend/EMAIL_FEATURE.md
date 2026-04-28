# Email Notification Feature

## Overview
EduroApp now automatically sends emails to users for:
1. **Login Confirmation** - When user successfully logs in
2. **Scholarship Results** - When user finds matching scholarships

## Configuration
- **Email**: anuranjsmanoj61@gmail.com
- **SMTP**: Gmail (smtp.gmail.com:587)
- **App Password**: Configured in `src/email_service.py`

## Email Types

### 1. Login Email
**Triggered**: When user logs in via `/api/auth/login`
**Contains**:
- Welcome message
- Login timestamp
- User name

### 2. Scholarship Results Email
**Triggered**: When user clicks "Find My Matches" via `/recommendations`
**Contains**:
- Number of matches found
- List of all scholarships with:
  - Match percentage
  - Scholarship title
  - Description snippet
  - Apply link
- Timestamp

## Testing

Run the test script:
```bash
cd backend
python test_email.py
```

This will send test emails to verify the configuration.

## API Integration

### Login Endpoint
```python
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```
✅ Sends login confirmation email automatically

### Recommendations Endpoint
```python
POST /recommendations
{
  "name": "John Doe",
  "email": "john@example.com",
  "education_level": "Undergraduate",
  "family_income": 50000,
  "category": "General",
  "religion": "Any",
  "gender": "Male"
}
```
✅ Sends scholarship results email automatically

## Error Handling
- Email failures are logged but don't block API responses
- Users still get results even if email fails
- Check backend logs for email errors

## Security Notes
- App password is used (not regular Gmail password)
- TLS encryption enabled
- Credentials stored in backend only
- Never exposed to frontend

## Deployment
Email service works on:
- ✅ Local development
- ✅ Azure VM deployment
- ✅ Docker containers

No additional configuration needed - it's ready to use!
