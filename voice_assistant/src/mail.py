"""Optional SMTP send for the assignment (dummy/test mailbox). Never log the password."""

from __future__ import annotations

import os
import re
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


def send_email(to_addr: str, body: str, subject: str = "Message from Lentswe") -> str:
    to_addr = (to_addr or "").strip()
    body = (body or "").strip()
    if not to_addr or "@" not in to_addr:
        return "I need a real email address, for example: send an email to test@example.com saying hello."
    if not body:
        return "Say what the email should say."
    host = os.getenv("SMTP_HOST", "").strip()
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_addr = (os.getenv("SMTP_FROM") or user).strip()
    try:
        port = int(os.getenv("SMTP_PORT", "587") or 587)
    except ValueError:
        port = 587
    if not host or not user or not password:
        return (
            "I did not send mail. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env "
            "(a dummy/test mailbox). I will not invent a successful send."
        )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception:
        return "SMTP refused the send. Check the test account in .env. I will not pretend it arrived."
    return f"I sent the test email to {to_addr}."


def try_send_email(user_text: str) -> str | None:
    text = (user_text or "").strip()
    match = re.search(
        r"(?:send (?:an )?email|email)\s+(?:to\s+)?(\S+@\S+)\s+(?:saying|that says|that|:)\s+(.+)",
        text,
        re.I,
    )
    if not match:
        if re.search(r"\b(send (?:an )?email|email)\b", text, re.I):
            return (
                "To email, say: send an email to test@example.com saying hello from Lentswe. "
                "Needs SMTP_* in .env."
            )
        return None
    return send_email(match.group(1).strip("<>,"), match.group(2).strip())
