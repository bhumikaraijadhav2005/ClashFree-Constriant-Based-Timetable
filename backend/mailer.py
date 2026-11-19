# backend/mailer.py
# ClashFree Institutional Email Dispatcher
# Supports SMTP delivery (Gmail, Office 365, University/College Mail Servers)
# with console fallback for local development and auditing.

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_mailer_config():
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", "").strip(),
        "password": os.getenv("SMTP_PASSWORD", "").strip(),
        "from_email": os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "no-reply@clashfree.edu")).strip(),
        "from_name": os.getenv("SMTP_FROM_NAME", "ClashFree Timetable Portal").strip(),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes"),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/"),
    }


def send_password_reset_email(to_email: str, recipient_name: str, reset_url: str) -> tuple[bool, str]:
    """
    Sends a password reset email to the recipient's institutional email address.
    If SMTP settings are unconfigured, logs the reset link to console and returns True for testing.
    """
    config = get_mailer_config()
    to_email = to_email.strip().lower()
    subject = "Reset Your ClashFree Account Password"

    # Plain text version for non-HTML mail readers
    text_content = f"""Hello {recipient_name or 'User'},

You requested a password reset for your ClashFree account ({to_email}).

To set a new password, open this secure link in your browser:
{reset_url}

This link is valid for 15 minutes. If you did not request this reset, you can safely ignore this email; your existing password will remain unchanged.

Best regards,
ClashFree Timetable Platform Administration
"""

    # Polished HTML version styled in dark navy / violet SaaS theme
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your Password</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; margin: 0; padding: 30px 15px; color: #f1f5f9;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table width="560" border="0" cellspacing="0" cellpadding="0" style="background-color: #111827; border: 1px solid #7c3aed; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);">
          <!-- Header -->
          <tr>
            <td style="padding: 28px 32px; background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border-bottom: 1px solid rgba(124, 58, 237, 0.2);">
              <div style="font-size: 22px; font-weight: 800; color: #a78bfa; letter-spacing: -0.5px;">⏰ ClashFree</div>
              <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Constraint-Based Timetable Scheduler</div>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 32px;">
              <h2 style="margin: 0 0 14px 0; color: #f8fafc; font-size: 19px; font-weight: 700;">Password Reset Request</h2>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin: 0 0 18px 0;">
                Hello <strong>{recipient_name or 'Faculty'}</strong>,
              </p>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin: 0 0 24px 0;">
                We received a request to reset the password for your ClashFree account (<strong style="color: #a78bfa;">{to_email}</strong>). Click the button below to choose a new password.
              </p>
              <!-- CTA Button -->
              <table border="0" cellspacing="0" cellpadding="0" style="margin: 28px 0;">
                <tr>
                  <td align="center" style="border-radius: 8px; background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%);">
                    <a href="{reset_url}" target="_blank" style="font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none; padding: 12px 28px; display: inline-block; border-radius: 8px;">
                      Reset Password &rarr;
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #94a3b8; font-size: 13px; line-height: 1.5; margin: 24px 0 12px 0;">
                If the button above does not work, copy and paste this link into your browser:
              </p>
              <div style="background-color: #030712; padding: 12px; border-radius: 6px; border: 1px solid #1f2937; word-break: break-all; font-family: monospace; font-size: 12px; color: #a78bfa;">
                {reset_url}
              </div>
              <p style="color: #64748b; font-size: 12px; line-height: 1.5; margin: 24px 0 0 0; border-top: 1px solid #1f2937; padding-top: 18px;">
                ⏰ This link will expire in <strong>15 minutes</strong> for security.<br>
                If you did not request a password reset, you can safely ignore this email — your account remains completely secure.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding: 16px 32px; background-color: #030712; border-top: 1px solid #1f2937; text-align: center; font-size: 12px; color: #475569;">
              ClashFree Timetable & Resource ERP &bull; Official Academic Portal
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # Always log the reset link to terminal for instant visibility and testing
    print(f"\n=======================================================")
    print(f"[ClashFree Mailer] Password reset link for {to_email}:")
    print(f"URL: {reset_url}")
    print(f"=======================================================\n")

    # If SMTP is configured, attempt real email transmission
    if config["host"] and config["user"]:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f'"{config["from_name"]}" <{config["from_email"]}>'
            msg["To"] = to_email

            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part1)
            msg.attach(part2)

            context = ssl.create_default_context()
            if config["port"] == 465:
                # SSL Direct Connection
                with smtplib.SMTP_SSL(config["host"], config["port"], context=context, timeout=15) as server:
                    server.ehlo()
                    if config["password"]:
                        server.login(config["user"], config["password"])
                    server.sendmail(config["from_email"], [to_email], msg.as_string())
            else:
                # STARTTLS Connection (port 587 or 25)
                with smtplib.SMTP(config["host"], config["port"], timeout=15) as server:
                    server.ehlo()
                    if config["use_tls"]:
                        server.starttls(context=context)
                        server.ehlo()
                    if config["password"]:
                        server.login(config["user"], config["password"])
                    server.sendmail(config["from_email"], [to_email], msg.as_string())

            return True, f"Password reset email sent to {to_email}."
        except Exception as e:
            err_msg = f"Failed to send email via SMTP ({e}). Reset link is logged in server console: {reset_url}"
            print(f"[ClashFree Mailer Warning] {err_msg}")
            return False, err_msg
    else:
        # Development / Sandbox mode: SMTP not set up yet
        return True, f"Password reset instructions generated. Link logged to server terminal."
