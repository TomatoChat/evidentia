# Email Configuration Setup

This guide will help you configure SMTP email sending for the Evidentia application.

## Gmail Setup (Recommended)

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Navigate to Security → 2-Step Verification
- Enable 2-Factor Authentication if not already enabled

### 2. Generate App Password
- Go to Google Account → Security → 2-Step Verification
- Scroll down to "App passwords"
- Click "Generate" and select "Mail" as the app
- Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 3. Update .env File
Add these lines to your `.env` file:

```bash
# SMTP Email Configuration
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
```

## Other Email Providers

### Outlook/Hotmail
```bash
SMTP_EMAIL=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_SERVER=smtp-mail.outlook.com
```

### Yahoo Mail
```bash
SMTP_EMAIL=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.mail.yahoo.com
```

### Custom SMTP Server
```bash
SMTP_EMAIL=your-email@yourdomain.com
SMTP_PASSWORD=your-password
SMTP_SERVER=mail.yourdomain.com
```

## Testing Email Configuration

1. Start the development server:
   ```bash
   ./start-dev.sh
   ```

2. Complete a brand analysis flow

3. Click "📧 Send Report to Email" - you should receive an email with:
   - HTML formatted report summary
   - Full JSON attachment with all analysis data
   - Professional branding

## Email Features

The sent email includes:
- **Executive Summary** with key metrics
- **Top 5 Recommendations** preview
- **Full JSON Report** as attachment
- **Professional HTML Design** with Evidentia branding
- **Plain Text Fallback** for email clients that don't support HTML

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Double-check your email and app password
   - Ensure 2FA is enabled for Gmail
   - Use app password, not your regular password

2. **"SMTP server not found"**
   - Verify the SMTP server address
   - Check if your network blocks SMTP ports

3. **"Permission denied"**
   - Some networks block outgoing SMTP traffic
   - Try using a different network or VPN

4. **Email not received**
   - Check spam/junk folder
   - Verify the recipient email is correct
   - Check server logs for error messages

### Debug Mode
The server will print email status to the console:
- ✅ "Report successfully sent to email@example.com"
- ❌ "Failed to send email: [error details]"

## Security Notes

- Never commit your `.env` file to version control
- Use app passwords instead of regular passwords
- Consider using environment variables in production
- The `.env` file is already in `.gitignore`