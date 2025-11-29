# How to Get OTP Codes (Development Mode)

## Problem
In development, email and SMS are mocked (not actually sent). You need to retrieve OTP codes to verify your account.

## Solution: 3 Easy Ways to Get Your OTP

### ✅ Method 1: Use the "Get My OTP Code" Button (EASIEST)

1. **Register** at: https://publisher-hub-4.preview.emergentagent.com/auth/register
2. You'll be redirected to the **Verify OTP** page
3. Look for the **yellow box** that says "📝 Development Mode"
4. Click the **"Get My OTP Code"** button
5. Your OTP will automatically fill in the input field!
6. Click **"Verify OTP"** to complete verification

**Screenshot Flow:**
```
Register → Verify Page → Yellow Box → Click "Get My OTP Code" → OTP Auto-fills → Click Verify
```

---

### Method 2: Use the API Endpoint Directly

**Step 1: Register a user**
```bash
curl -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "password": "Test@123456"
  }'
```

**Step 2: Get OTP codes**
```bash
# Using email
curl "https://publisher-hub-4.preview.emergentagent.com/api/auth/dev/get-otp/john@example.com"

# OR using phone
curl "https://publisher-hub-4.preview.emergentagent.com/api/auth/dev/get-otp/%2B1234567890"
```

**Response:**
```json
{
  "user_email": "john@example.com",
  "user_phone": "+1234567890",
  "email_otp": "123456",
  "email_otp_expires": "2024-01-01T10:40:00+00:00",
  "sms_otp": "789012",
  "sms_otp_expires": "2024-01-01T10:40:00+00:00",
  "note": "This is a development endpoint. Remove in production!"
}
```

**Step 3: Use the OTP to verify**
```bash
# Verify with email OTP
curl -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "john@example.com",
    "otp_code": "123456",
    "otp_type": "email"
  }'

# OR verify with SMS OTP
curl -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "+1234567890",
    "otp_code": "789012",
    "otp_type": "sms"
  }'
```

---

### Method 3: Check Backend Logs

```bash
# View OTP codes as they're generated
tail -f /var/log/supervisor/backend.out.log | grep -A 5 "OTP"
```

**Example output:**
```
==================================================
📧 EMAIL OTP SENT
To: john@example.com
OTP Code: 123456
Valid for: 10 minutes
==================================================

==================================================
📱 SMS OTP SENT
To: +1234567890
OTP Code: 789012
Valid for: 10 minutes
==================================================
```

---

## Complete Registration Flow (UI)

### Step-by-Step:

1. **Go to Registration**
   - Visit: https://publisher-hub-4.preview.emergentagent.com/auth/register

2. **Fill the Form**
   ```
   First Name: John
   Last Name: Doe
   Email: john@example.com
   Phone: +1234567890
   Password: Test@123456
   ```
   *(Business fields are optional)*

3. **Click "Create Account"**
   - You'll be redirected to verification page

4. **Get Your OTP**
   - Click the yellow **"Get My OTP Code"** button
   - OTP will auto-fill

5. **Verify**
   - Click **"Verify OTP"**
   - Success! You can now login

6. **Login**
   - Visit: https://publisher-hub-4.preview.emergentagent.com/auth/login
   - Use your email/phone and password

---

## Troubleshooting

### "No OTP found. Please resend OTP first."
**Solution:** Click the "Resend OTP" link, wait a few seconds, then click "Get My OTP Code" again.

### "User not found"
**Solution:** Make sure you completed registration first.

### "OTP has expired"
**Solution:** OTPs expire after 10 minutes. Click "Resend OTP" to get a new one.

### "Invalid OTP code"
**Solution:** 
- Make sure you're using the correct OTP (email vs SMS)
- Switch tabs if needed (Email tab vs SMS tab)
- Get a fresh OTP using the button

### Backend not showing OTP
**Solution:**
```bash
# Restart backend
sudo supervisorctl restart backend

# Check logs
tail -f /var/log/supervisor/backend.out.log
```

---

## Quick Test Script

Here's a complete test you can run:

```bash
#!/bin/bash

# 1. Register
echo "1. Registering user..."
curl -s -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test123@example.com",
    "phone": "+9876543210",
    "password": "Test@123456"
  }' | jq

echo -e "\n2. Getting OTP codes..."
sleep 2
OTP_RESPONSE=$(curl -s "https://publisher-hub-4.preview.emergentagent.com/api/auth/dev/get-otp/test123@example.com")
echo $OTP_RESPONSE | jq

EMAIL_OTP=$(echo $OTP_RESPONSE | jq -r '.email_otp')
echo -e "\n3. Email OTP: $EMAIL_OTP"

echo -e "\n4. Verifying with OTP..."
curl -s -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{
    \"identifier\": \"test123@example.com\",
    \"otp_code\": \"$EMAIL_OTP\",
    \"otp_type\": \"email\"
  }" | jq

echo -e "\n5. Logging in..."
curl -s -X POST https://publisher-hub-4.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "test123@example.com",
    "password": "Test@123456"
  }' | jq
```

Save this as `test_auth.sh`, make it executable (`chmod +x test_auth.sh`), and run it (`./test_auth.sh`).

---

## Important Notes

⚠️ **Development Endpoint Warning**: The `/api/auth/dev/get-otp/{identifier}` endpoint is ONLY for development. It should be removed or disabled in production!

✅ **In Production**: You'll configure real SMTP for email and Twilio for SMS. See `/app/AUTH_SYSTEM_DOCUMENTATION.md` for setup instructions.

---

## Need Help?

- **Full Documentation**: `/app/AUTH_SYSTEM_DOCUMENTATION.md`
- **Check if services are running**: `sudo supervisorctl status`
- **Restart services**: `sudo supervisorctl restart backend frontend`
- **View logs**: `tail -f /var/log/supervisor/backend.err.log`
