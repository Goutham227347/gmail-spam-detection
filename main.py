import imaplib
import email

def fetch_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox",'[Gmail]/Spam')

    _, data = mail.search(None, "ALL")
    mail_ids = data[0].split()[-10:]  # Last 10 emails

    emails = []
    for num in mail_ids:
        _, msg_data = mail.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg["subject"]
                if msg.is_multipart():
                    content = ''
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            content += part.get_payload(decode=True).decode(errors="ignore")
                else:
                    content = msg.get_payload(decode=True).decode(errors="ignore")
                emails.append((subject, content))
    return emails
