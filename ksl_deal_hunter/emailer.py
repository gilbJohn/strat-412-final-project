"""
emailer.py — Send an HTML digest email of top KSL deals via Gmail SMTP.

Requires in .env:
  GMAIL_ADDRESS      — your Gmail address (sender)
  GMAIL_APP_PASSWORD — 16-char App Password (not your regular password)
  EMAIL_TO           — recipient address (can be same as sender)
"""

import os
import re
import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from database import mark_emailed


def _reply_url(listing_url: str) -> str | None:
    """
    Build the Craigslist reply page URL from a listing URL.
    e.g. https://saltlakecity.craigslist.org/fuo/d/midvale-queen-mattress/7923451580.html
      -> https://saltlakecity.craigslist.org/reply/slc/fuo/7923451580
    The area code (slc) is extracted from the subdomain.
    """
    m = re.match(
        r'(https?://(\w+)\.craigslist\.org)/(\w+)/d/[^/]+/(\d+)\.html', listing_url
    )
    if not m:
        return None
    base, subdomain, category, posting_id = m.group(1), m.group(2), m.group(3), m.group(4)
    # Craigslist area codes are typically the first 3 letters of the subdomain
    # but some are longer (e.g. newyork -> nyc). For SLC it's slc.
    area_map = {"saltlakecity": "slc"}
    area = area_map.get(subdomain, subdomain[:3])
    return f"{base}/reply/{area}/{category}/{posting_id}"

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# ── Score badge colours ────────────────────────────────────────────────────────
def _badge_colour(score: int) -> str:
    if score >= 9:
        return "#22c55e"   # green
    if score >= 7:
        return "#14b8a6"   # teal
    return "#eab308"       # yellow (score 6)


def _build_html(deals: list) -> str:
    """Render the full HTML email body."""
    by_cat: dict[str, list] = {}
    for deal in deals:
        by_cat.setdefault(deal["category"], []).append(deal)

    sections = []
    for cat, items in by_cat.items():
        cards = []
        for d in items:
            colour = _badge_colour(d["score"])
            reason = d.get("reason") or ""
            reply = _reply_url(d["url"]) or d["url"]
            cards.append(f"""
            <tr>
              <td style="padding:0 0 10px 0;">
                <table style="width:100%;border-collapse:collapse;
                               background:#0f1929;border-radius:8px;
                               border:1px solid #1e2a3a;">
                  <tr>
                    <td style="padding:12px 16px;">
                      <table style="width:100%;border-collapse:collapse;">
                        <tr>
                          <td style="vertical-align:top;width:1%;">
                            <span style="
                              display:inline-block;background:{colour};
                              color:#07070f;font-weight:800;padding:3px 10px;
                              border-radius:5px;font-size:13px;
                              font-family:monospace;white-space:nowrap;
                              margin-right:10px;
                            ">{d['score']}/10</span>
                          </td>
                          <td style="vertical-align:top;">
                            <a href="{d['url']}" style="
                              color:#e2e8f0;text-decoration:none;font-weight:600;
                              font-size:14px;line-height:1.4;
                            ">{d['title']}</a>
                          </td>
                          <td style="vertical-align:top;text-align:right;width:1%;">
                            <span style="
                              color:#4ade80;font-family:monospace;font-weight:700;
                              font-size:15px;white-space:nowrap;padding-left:12px;
                            ">{d['price']}</span>
                          </td>
                        </tr>
                        {f'<tr><td></td><td colspan="2" style="padding-top:6px;color:#64748b;font-size:12px;line-height:1.5;">{reason}</td></tr>' if reason else ''}
                        <tr>
                          <td></td>
                          <td colspan="2" style="padding-top:8px;">
                            <a href="{d['url']}" style="
                              display:inline-block;background:#1e3a5f;
                              color:#93c5fd;text-decoration:none;font-size:12px;
                              padding:4px 12px;border-radius:4px;font-weight:600;
                              border:1px solid #2563eb;
                            ">View listing →</a>
                            &nbsp;<a href="{reply}" style="
                              display:inline-block;background:#1e3050;
                              color:#a78bfa;text-decoration:none;font-size:12px;
                              padding:4px 12px;border-radius:4px;font-weight:600;
                              border:1px solid #7c3aed;
                            ">Reply to seller →</a>
                            {f'&nbsp;<a href="mailto:{d["seller_email"]}" style="display:inline-block;background:#14532d;color:#4ade80;text-decoration:none;font-size:12px;padding:4px 12px;border-radius:4px;font-weight:600;border:1px solid #16a34a;">{d["seller_email"]}</a>' if d.get("seller_email") else ''}
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>""")

        sections.append(f"""
        <tr><td style="padding-top:24px;padding-bottom:8px;">
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="
                border-left:3px solid #3b82f6;padding:2px 0 2px 10px;
              ">
                <span style="
                  color:#93c5fd;font-family:monospace;font-weight:700;
                  font-size:15px;text-transform:uppercase;letter-spacing:.05em;
                ">{cat}</span>
                <span style="color:#475569;font-size:12px;margin-left:8px;">
                  {len(items)} deal{'s' if len(items) != 1 else ''}
                </span>
              </td>
            </tr>
          </table>
        </td></tr>
        {"".join(cards)}""")

    today = date.today().strftime("%B %d, %Y")
    body = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#07070f;color:#e2e8f0;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table style="width:100%;background:#07070f;" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:24px 16px;">
      <table style="max-width:680px;width:100%;" cellpadding="0" cellspacing="0">

        <!-- Header -->
        <tr><td style="
          background:linear-gradient(135deg,#0f2444 0%,#0a1628 100%);
          border:1px solid #1e3a5f;border-radius:10px;
          padding:20px 24px;margin-bottom:16px;
        ">
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td>
                <div style="font-size:20px;font-weight:800;color:#f8fafc;
                            letter-spacing:-.02em;">
                  🛒 KSL Deal Hunter
                </div>
                <div style="color:#64748b;font-family:monospace;font-size:13px;
                            margin-top:3px;">
                  {today}
                </div>
              </td>
              <td style="text-align:right;">
                <span style="
                  background:#1e3a5f;color:#93c5fd;font-family:monospace;
                  font-weight:700;font-size:14px;padding:6px 14px;
                  border-radius:20px;border:1px solid #2563eb;
                ">{len(deals)} deals</span>
              </td>
            </tr>
          </table>
        </td></tr>

        <!-- Deals -->
        <tr><td>
          <table style="width:100%;border-collapse:collapse;">
            {body}
          </table>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding-top:20px;border-top:1px solid #1e2a3a;
                       text-align:center;">
          <p style="color:#334155;font-size:11px;font-family:monospace;margin:0;">
            Scores by Claude AI &nbsp;·&nbsp;
            <a href="https://classifieds.ksl.com" style="color:#475569;">
              classifieds.ksl.com
            </a>
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_digest(deals: list):
    """
    Send the HTML digest for `deals` via Gmail SMTP SSL.
    Marks all sent listings as emailed in the DB.
    """
    if not deals:
        print("    No deals to email.")
        return

    gmail_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    missing = [
        name for name, val in [
            ("GMAIL_ADDRESS", gmail_address),
            ("GMAIL_APP_PASSWORD", app_password),
            ("EMAIL_TO", email_to),
        ] if not val
    ]
    if missing:
        raise EnvironmentError(
            f"Missing required env vars: {', '.join(missing)}"
        )

    today = date.today().strftime("%b %d")
    subject = f"🛒 KSL Deal Hunter — {len(deals)} finds · {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = email_to

    # Plain-text fallback
    plain_lines = [f"KSL Deal Hunter — {len(deals)} finds · {today}", ""]
    current_cat = None
    for d in deals:
        if d["category"] != current_cat:
            current_cat = d["category"]
            plain_lines.append(f"\n== {current_cat} ==")
        seller = d.get("seller_email") or ""
        reply = _reply_url(d["url"]) or d["url"]
        plain_lines.append(
            f"  [{d['score']}/10] {d['title']} — {d['price']}\n"
            f"  {d.get('reason','')}\n"
            f"  Listing: {d['url']}\n"
            f"  Reply:   {reply}"
            + (f"\n  Contact: {seller}" if seller else "")
        )
    msg.attach(MIMEText("\n".join(plain_lines), "plain"))
    msg.attach(MIMEText(_build_html(deals), "html"))

    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl_context) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, email_to, msg.as_string())

    mark_emailed([d["url"] for d in deals])
    print(f"    Email sent to {email_to}")
