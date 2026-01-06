# Render Environment Setup Guide

## Environment Variables Configuration

To fix the email issues in production, you need to configure the following environment variables in your Render dashboard.

### Step-by-Step Instructions

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Select your HHH backend service (`hhh-backend`)

2. **Open Environment Variables**
   - Click on the **Environment** tab in the left sidebar
   - Click **Add Environment Variable** button

3. **Add Required Variables**

   Add each of the following environment variables:

   #### Variable 1: RESEND_API_KEY
   ```
   Key: RESEND_API_KEY
   Value: re_VoEze1QK_3BYNfKrPT88bgYE6JsZeaEYC
   ```
   **Purpose:** Authenticates with Resend API for sending emails

   #### Variable 2: FROM_EMAIL
   ```
   Key: FROM_EMAIL
   Value: onboarding@resend.dev
   ```
   **Purpose:** The "From" email address for all transactional emails

   #### Variable 3: FRONTEND_URL (CRITICAL FIX)
   ```
   Key: FRONTEND_URL
   Value: https://rakesh-arrepu.github.io/HHH
   ```
   **Purpose:** Used to generate correct links in emails (currently broken with localhost URL)

   **⚠️ IMPORTANT:** This is the fix for Issue #1 - Welcome emails currently have localhost links!

   #### Variable 4: SECRET_KEY (if not already set)
   ```
   Key: SECRET_KEY
   Value: <your-existing-secret-key>
   ```
   **Purpose:** Used for session tokens and password reset tokens

   **Note:** Check if this is already set. If yes, don't change it.

4. **Save Changes**
   - Click **Save Changes** button
   - Render will automatically redeploy your service

5. **Wait for Deployment**
   - Wait for the deployment to complete (usually 2-3 minutes)
   - Check the deployment logs for any errors

---

## Verification Steps

After deployment completes, verify the fixes are working:

### Test 1: Check Environment Variables are Loaded

View your Render logs and look for startup messages. You should NOT see:
```
Email service not configured (RESEND_API_KEY not set)
```

### Test 2: Test Welcome Email (Issue #1 Fix)

1. Register a new test user in production: https://rakesh-arrepu.github.io/HHH
2. Check your Render logs for:
   ```
   ✓ Welcome email sent successfully to [email]
   ```
3. Check your inbox for the welcome email
4. **Verify the "Get Started" link** points to `https://rakesh-arrepu.github.io/HHH/#/` (NOT localhost!)

### Test 3: Test Multiple Members (Issue #2 Fix)

1. Create a test group
2. Add 3 members rapidly (within a few seconds)
3. Check Render logs for:
   ```
   Rate limiting: waiting 0.XXs before sending to [email]
   ✓ Both member-added emails sent successfully for group '[name]' (ID: X)
   ```
4. **Verify all 6 emails were received** (3 members × 2 emails each)
5. Check that there are NO "rate limit exceeded" errors

### Test 4: Monitor Error Logs

Check Render logs for any CRITICAL errors:
```
CRITICAL: Failed to send email to [email]: [error]
```

If you see these, investigate the specific error message.

---

## Expected Log Output (Success)

After fixes, your Render logs should show:

### Successful Welcome Email
```
Email sent successfully to user@example.com, id: abc123, subject: Welcome to HHH Daily Tracker!
✓ Welcome email sent successfully to user@example.com
```

### Successful Member Addition
```
Email sent successfully to member@example.com, id: abc123, subject: You've been added to 'Family Fitness'
Rate limiting: waiting 0.50s before sending to owner@example.com
Email sent successfully to owner@example.com, id: def456, subject: New member added to 'Family Fitness'
✓ Both member-added emails sent successfully for group 'Family Fitness' (ID: 5)
```

### Successful Ownership Transfer
```
Email sent successfully to newowner@example.com, id: abc123, subject: You're now the owner of 'Team Group'
Rate limiting: waiting 0.48s before sending to prevowner@example.com
Email sent successfully to prevowner@example.com, id: def456, subject: You've transferred ownership of 'Team Group'
✓ Both ownership transfer emails sent successfully for group 'Team Group' (ID: 8)
```

---

## Troubleshooting

### Issue: Still seeing "Email service not configured"

**Solution:**
1. Verify `RESEND_API_KEY` is set in Render Environment tab
2. Check for typos in the key
3. Ensure no extra spaces in the value
4. Redeploy the service manually

### Issue: Emails sent but links still point to localhost

**Solution:**
1. Verify `FRONTEND_URL` is set to `https://rakesh-arrepu.github.io/HHH` (no trailing slash)
2. Check for typos
3. Redeploy the service
4. Clear your email client cache and re-register

### Issue: Rate limit errors still occurring

**Solution:**
1. Check that you deployed the latest code with rate limiting fix
2. Look for this in logs: `Rate limiting: waiting X.XXs`
3. If not present, the fix wasn't deployed
4. Run `git pull` on Render or trigger manual deploy

### Issue: No emails being sent at all

**Solution:**
1. Check Resend dashboard: https://resend.com/emails
2. Verify API key is correct
3. Check if you've exceeded free tier limits (100/day, 3,000/month)
4. Look for error messages in Render logs starting with "CRITICAL:"

### Issue: Emails going to spam

**Solution:**
1. This is expected for `onboarding@resend.dev` (test domain)
2. For production, configure a custom domain in Resend
3. Add SPF and DKIM records
4. See: https://resend.com/docs/dashboard/domains/introduction

---

## Production Checklist

Before considering the fixes complete, verify:

- [ ] `FRONTEND_URL` set to production URL (NOT localhost)
- [ ] `RESEND_API_KEY` configured in Render
- [ ] `FROM_EMAIL` configured in Render
- [ ] Service successfully redeployed
- [ ] Welcome email test passed with correct links
- [ ] Multiple member addition test passed (no rate limit errors)
- [ ] All emails received in inbox (check spam folder too)
- [ ] Render logs show success messages, not CRITICAL errors
- [ ] Rate limiting delays visible in logs (e.g., "waiting 0.50s")

---

## Monitoring

### Daily Checks

Monitor your Resend dashboard for:
- Email volume (stay under 100/day, 3,000/month)
- Delivery rate (should be ~100%)
- Bounce rate (should be <5%)
- Spam complaints (should be 0%)

### Weekly Checks

Review Render logs for:
- Any CRITICAL email errors
- Rate limiting patterns
- Overall email success rate

---

## Support

If issues persist:

1. **Check Render Logs:**
   ```
   Dashboard → Your Service → Logs tab
   ```

2. **Check Resend Dashboard:**
   ```
   https://resend.com/emails
   ```

3. **Test Locally First:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   # Test registration at http://localhost:8000
   ```

4. **GitHub Issues:**
   - File a bug report at: https://github.com/rakesh-arrepu/HHH/issues
   - Include: Render logs, error messages, steps to reproduce

---

## Additional Configuration (Optional)

### Custom Domain for Emails

To avoid spam folder issues, configure a custom domain:

1. Go to Resend Dashboard: https://resend.com/domains
2. Add your domain (e.g., `notifications.yourdomain.com`)
3. Add DNS records (SPF, DKIM)
4. Update `FROM_EMAIL` environment variable to use custom domain
5. Redeploy Render service

### Email Monitoring

Set up monitoring for email failures:

1. Configure Resend webhooks in dashboard
2. Create endpoint in backend to receive webhook events
3. Log failed emails to monitoring service (e.g., Sentry)
4. Set up alerts for email failures

---

## Environment Variable Summary

| Variable | Value | Purpose | Status |
|----------|-------|---------|--------|
| `RESEND_API_KEY` | `re_VoEze1QK_...` | Resend authentication | Required |
| `FROM_EMAIL` | `onboarding@resend.dev` | Sender email address | Required |
| `FRONTEND_URL` | `https://rakesh-arrepu.github.io/HHH` | Frontend URL for links | **CRITICAL FIX** |
| `SECRET_KEY` | `<existing-value>` | Session/token encryption | Required (check if exists) |
| `DATABASE_URL` | `<existing-value>` | Database connection | Already configured |
| `ALLOWED_ORIGINS` | `<existing-value>` | CORS origins | Already configured |

**Last Updated:** 2026-01-06
