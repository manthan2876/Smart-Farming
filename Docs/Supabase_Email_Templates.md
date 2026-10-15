# Supabase Custom Email Templates for Smart Farming

These responsive HTML email templates are styled specifically for **Smart Farming** (`#166534` emerald farm green branding, clean typography, mobile responsiveness, and dark-mode-safe styling).

To apply them in your Supabase project:
1. Open your **Supabase Dashboard** ([DEV](https://supabase.com/dashboard/project/zgsbxzwyumvxazbroiws/auth/templates) or [PROD](https://supabase.com/dashboard/project/ntqevjzjhntkilmknrfh/auth/templates)).
2. Go to **Authentication** &rarr; **URL Configuration**:
   - Set **Site URL** to: `http://localhost:5173` (or your production frontend URL).
   - Add to **Redirect URLs**:
     - `http://localhost:5173/**`
     - `http://localhost:5173/auth/verify-email`
     - `http://localhost:5173/auth/reset-password`
3. Go to **Authentication** &rarr; **Email Templates**:
   - Select each template tab, paste the corresponding **Subject** and **HTML Body**, then click **Save**.

> [!NOTE]
> **Understanding `otp_expired` or "Email link is invalid or has expired":**
> - In Supabase Auth, generating a new confirmation email or resending immediately invalidates any previous tokens. If you click a link from an earlier email, Supabase rejects it with `error_code=otp_expired`.
> - Always use the **most recent email** received in your inbox.
> - Alternatively, users can enter the **6-digit confirmation code** (`{{ .Token }}`) shown in the email directly into the verification screen.

---

## 1. Confirm Signup (`Confirm signup`)
> **Triggered when**: A new user registers using their email address.

**Subject Line:**
```text
🌱 Confirm your Smart Farming account
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Confirm Your Smart Farming Account</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #dcfce7; color: #15803d; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .btn-container { text-align: center; margin: 28px 0; }
    .btn { display: inline-block; background-color: #16a34a; color: #ffffff !important; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 36px; border-radius: 8px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25); }
    .otp-box { background-color: #f0fdf4; border: 1px dashed #86efac; border-radius: 8px; padding: 16px; text-align: center; margin: 24px 0; }
    .otp-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #15803d; font-weight: 700; margin-bottom: 6px; }
    .otp-code { font-family: 'Courier New', Courier, monospace; font-size: 28px; font-weight: 800; color: #14532d; letter-spacing: 6px; }
    .info-box { background-color: #f8fafc; border-left: 4px solid #16a34a; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin: 24px 0 0 0; line-height: 1.5; }
    .alt-link { font-size: 12px; color: #64748b; word-break: break-all; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
    .alt-link a { color: #16a34a; text-decoration: underline; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Account Verification</span>
        <h1>Welcome to Smart Farming!</h1>
        <p>Thank you for creating an account. To complete your registration and activate AI leaf diagnostic scans and localized crop advisories, please confirm your email address.</p>
        
        <div class="btn-container">
          <a href="{{ .ConfirmationURL }}" class="btn" target="_blank">Confirm Email Address</a>
        </div>

        <div class="otp-box">
          <div class="otp-label">Or use this 6-digit confirmation code</div>
          <div class="otp-code">{{ .Token }}</div>
        </div>

        <div class="info-box">
          <strong>Security note:</strong> This confirmation link expires in 24 hours. If you did not create a Smart Farming account, please disregard this email.
        </div>

        <div class="alt-link">
          If the button above does not work, copy and paste this link into your browser:<br>
          <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

---

## 2. Invite User (`Invite user`)
> **Triggered when**: An administrator or agronomist invites a farmer or staff member to the platform.

**Subject Line:**
```text
🌱 You've been invited to Smart Farming
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>You Have Been Invited to Smart Farming</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #e0f2fe; color: #0369a1; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .feature-list { background-color: #f8fafc; border-radius: 8px; padding: 18px 20px; margin: 22px 0; border: 1px solid #e2e8f0; }
    .feature-item { font-size: 14px; color: #334155; margin-bottom: 10px; display: flex; align-items: center; }
    .feature-item:last-child { margin-bottom: 0; }
    .btn-container { text-align: center; margin: 28px 0; }
    .btn { display: inline-block; background-color: #16a34a; color: #ffffff !important; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 36px; border-radius: 8px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25); }
    .info-box { background-color: #f8fafc; border-left: 4px solid #0369a1; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin: 24px 0 0 0; line-height: 1.5; }
    .alt-link { font-size: 12px; color: #64748b; word-break: break-all; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
    .alt-link a { color: #16a34a; text-decoration: underline; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Team Invitation</span>
        <h1>You're invited to join Smart Farming</h1>
        <p>You have been invited to collaborate on the Smart Farming platform. Join agronomists, researchers, and farmers in real-time foliar disease diagnostics and management.</p>
        
        <div class="feature-list">
          <div class="feature-item">🌾 <strong>Computer-Vision Leaf Disease Scans:</strong> Real-time pathogen detection</div>
          <div class="feature-item">🌦️ <strong>Microclimate Weather Forecasts:</strong> Localized spraying advisories</div>
          <div class="feature-item">🧪 <strong>Agronomist Expert Review:</strong> Verified multi-tiered treatment plans</div>
        </div>

        <p>Click the button below to accept your invitation and create your account password:</p>

        <div class="btn-container">
          <a href="{{ .ConfirmationURL }}" class="btn" target="_blank">Accept Invitation</a>
        </div>

        <div class="info-box">
          <strong>Need assistance?</strong> If you were not expecting this invitation, you can safely ignore this email.
        </div>

        <div class="alt-link">
          If the button above does not work, copy and paste this link into your browser:<br>
          <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

---

## 3. Magic Link with OTP (`Magic link`)
> **Triggered when**: A user signs in using a passwordless Magic Link or Email OTP code.

**Subject Line:**
```text
🌱 Your Smart Farming login code & link
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Smart Farming Login Link</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #fef3c7; color: #92400e; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .otp-box { background: linear-gradient(180deg, #f0fdf4 0%, #dcfce7 100%); border: 2px solid #86efac; border-radius: 10px; padding: 20px; text-align: center; margin: 26px 0; }
    .otp-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #166534; font-weight: 700; margin-bottom: 8px; }
    .otp-code { font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; color: #14532d; letter-spacing: 8px; }
    .btn-container { text-align: center; margin: 26px 0; }
    .btn { display: inline-block; background-color: #16a34a; color: #ffffff !important; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 36px; border-radius: 8px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25); }
    .info-box { background-color: #f8fafc; border-left: 4px solid #f59e0b; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin: 24px 0 0 0; line-height: 1.5; }
    .alt-link { font-size: 12px; color: #64748b; word-break: break-all; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
    .alt-link a { color: #16a34a; text-decoration: underline; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Instant Sign In</span>
        <h1>Sign In to Smart Farming</h1>
        <p>We received a passwordless login request. You can enter the 6-digit verification code below on the login screen, or click the direct sign-in button.</p>

        <div class="otp-box">
          <div class="otp-label">Your 6-Digit One-Time Code</div>
          <div class="otp-code">{{ .Token }}</div>
        </div>

        <div class="btn-container">
          <a href="{{ .ConfirmationURL }}" class="btn" target="_blank">Sign In Instantly</a>
        </div>

        <div class="info-box">
          <strong>Security note:</strong> This code and login link are valid for <strong>15 minutes</strong> and can only be used once. If you did not attempt to sign in, your account is safe and you can ignore this email.
        </div>

        <div class="alt-link">
          If the button above does not work, copy and paste this link into your browser:<br>
          <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

---

## 4. Change Email Address (`Change email address`)
> **Triggered when**: A user (including phone-registered accounts) updates or links an email address from Settings.

**Subject Line:**
```text
🌱 Confirm your email address change - Smart Farming
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Confirm Your Email Address Change</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #dcfce7; color: #15803d; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .email-change-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin: 20px 0; font-size: 14px; }
    .email-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
    .email-row:last-child { margin-bottom: 0; }
    .email-label { color: #64748b; font-weight: 600; }
    .email-val { color: #0f172a; font-weight: 700; word-break: break-all; }
    .btn-container { text-align: center; margin: 28px 0; }
    .btn { display: inline-block; background-color: #16a34a; color: #ffffff !important; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 36px; border-radius: 8px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25); }
    .otp-box { background-color: #f0fdf4; border: 1px dashed #86efac; border-radius: 8px; padding: 14px; text-align: center; margin: 20px 0; }
    .otp-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #15803d; font-weight: 700; margin-bottom: 4px; }
    .otp-code { font-family: 'Courier New', Courier, monospace; font-size: 26px; font-weight: 800; color: #14532d; letter-spacing: 6px; }
    .info-box { background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #991b1b; margin: 24px 0 0 0; line-height: 1.5; }
    .alt-link { font-size: 12px; color: #64748b; word-break: break-all; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
    .alt-link a { color: #16a34a; text-decoration: underline; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Email Update</span>
        <h1>Confirm your new email address</h1>
        <p>A request was made to update the email address linked to your Smart Farming account.</p>

        <div class="email-change-box">
          <table width="100%">
            <tr>
              <td style="color:#64748b; font-weight:600; padding:4px 0;">New Email:</td>
              <td style="color:#166534; font-weight:700; text-align:right; padding:4px 0;">{{ .NewEmail }}</td>
            </tr>
            <tr>
              <td style="color:#64748b; font-weight:600; padding:4px 0;">Current:</td>
              <td style="color:#64748b; text-align:right; padding:4px 0;">{{ .Email }}</td>
            </tr>
          </table>
        </div>

        <p>Please click the button below to confirm that this new email address belongs to you and link it to your account:</p>

        <div class="btn-container">
          <a href="{{ .ConfirmationURL }}" class="btn" target="_blank">Confirm Email Change</a>
        </div>

        <div class="otp-box">
          <div class="otp-label">Verification Code</div>
          <div class="otp-code">{{ .Token }}</div>
        </div>

        <div class="info-box">
          <strong>Did not request this change?</strong> If you did not initiate this email update, please log into your Smart Farming settings immediately or reset your password to secure your account.
        </div>

        <div class="alt-link">
          If the button above does not work, copy and paste this link into your browser:<br>
          <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

---

## 5. Password Reset (`Reset password`)
> **Triggered when**: A user requests a password recovery link from the login page.

**Subject Line:**
```text
🌱 Reset your Smart Farming password
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Smart Farming Password</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #fef3c7; color: #92400e; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .btn-container { text-align: center; margin: 28px 0; }
    .btn { display: inline-block; background-color: #16a34a; color: #ffffff !important; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 36px; border-radius: 8px; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25); }
    .otp-box { background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 14px; text-align: center; margin: 20px 0; }
    .otp-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; font-weight: 700; margin-bottom: 4px; }
    .otp-code { font-family: 'Courier New', Courier, monospace; font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: 6px; }
    .info-box { background-color: #f8fafc; border-left: 4px solid #f59e0b; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin: 24px 0 0 0; line-height: 1.5; }
    .alt-link { font-size: 12px; color: #64748b; word-break: break-all; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
    .alt-link a { color: #16a34a; text-decoration: underline; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Password Recovery</span>
        <h1>Reset your password</h1>
        <p>We received a request to reset the password for your Smart Farming account (<strong>{{ .Email }}</strong>). Click the button below to choose a new password:</p>

        <div class="btn-container">
          <a href="{{ .ConfirmationURL }}" class="btn" target="_blank">Reset Password</a>
        </div>

        <div class="otp-box">
          <div class="otp-label">Or enter this recovery token</div>
          <div class="otp-code">{{ .Token }}</div>
        </div>

        <div class="info-box">
          <strong>Security note:</strong> This password reset link is valid for <strong>15 minutes</strong>. If you did not request a password reset, you can safely ignore this email—your account credentials remain unchanged.
        </div>

        <div class="alt-link">
          If the button above does not work, copy and paste this link into your browser:<br>
          <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

---

## 6. Reauthentication (`Reauthentication`)
> **Triggered when**: A user performs a sensitive account action requiring fresh verification.

**Subject Line:**
```text
🌱 Confirm your identity on Smart Farming
```

**HTML Body:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Confirm Your Identity</title>
  <style>
    body { margin: 0; padding: 0; background-color: #f4f6f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    table { border-collapse: collapse; }
    .wrapper { width: 100%; table-layout: fixed; background-color: #f4f6f4; padding: 36px 12px; }
    .main-card { max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05); }
    .header { background: linear-gradient(135deg, #14532d 0%, #166534 100%); padding: 32px 28px; text-align: center; }
    .header-logo { font-size: 26px; font-weight: 800; color: #ffffff; text-decoration: none; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 13px; color: #bbf7d0; margin-top: 6px; letter-spacing: 0.3px; }
    .content { padding: 36px 32px; color: #1e293b; }
    .badge { display: inline-block; background-color: #fee2e2; color: #b91c1c; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }
    h1 { margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.3; }
    p { margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #334155; }
    .otp-box { background-color: #fef2f2; border: 2px dashed #fca5a5; border-radius: 10px; padding: 22px; text-align: center; margin: 26px 0; }
    .otp-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #991b1b; font-weight: 700; margin-bottom: 8px; }
    .otp-code { font-family: 'Courier New', Courier, monospace; font-size: 34px; font-weight: 800; color: #7f1d1d; letter-spacing: 8px; }
    .info-box { background-color: #f8fafc; border-left: 4px solid #ef4444; padding: 14px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin: 24px 0 0 0; line-height: 1.5; }
    .footer { background-color: #f8fafc; padding: 24px 28px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <div class="header-logo">🌱 Smart Farming</div>
        <div class="header-subtitle">AI Plant Diagnostics & Agronomic Guidance</div>
      </div>
      <div class="content">
        <span class="badge">Security Verification</span>
        <h1>Confirm your identity</h1>
        <p>A sensitive account operation (such as updating security settings or exporting farm telemetry) was initiated on your Smart Farming account.</p>
        <p>Enter this verification code in your browser to confirm your identity:</p>

        <div class="otp-box">
          <div class="otp-label">Reauthentication Code</div>
          <div class="otp-code">{{ .Token }}</div>
        </div>

        <div class="info-box">
          <strong>Security alert:</strong> This code is single-use and will expire in <strong>5 minutes</strong>. Never share this code with anyone. If you did not initiate this action, someone may be attempting unauthorized changes to your account.
        </div>
      </div>
      <div class="footer">
        <strong>Smart Farming Platform</strong> &bull; IT452 Minor Project &bull; SIH 25099<br>
        BVM Engineering College, Gujarat, India<br>
        This is an automated system message. Please do not reply directly to this email.
      </div>
    </div>
  </div>
</body>
</html>
```

