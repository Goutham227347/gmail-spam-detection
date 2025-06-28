import imaplib
import email
from email.header import decode_header
import re

# Add email_address and password as parameters to the function
def fetch_emails(email_address, password):
    """
    Fetches the latest 10 emails from the inbox and spam folders of a Gmail account.

    Args:
        email_address (str): The Gmail address.
        password (str): The Gmail App Password.

    Returns:
        list: A list of tuples, where each tuple contains (subject, content).
    """
    emails = []
    mail = None # Initialize mail to None

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        # Use the passed email_address and password for login
        mail.login(email_address, password)

        # List of mailboxes to search
        mailboxes_to_search = ["inbox", "[Gmail]/Spam"]

        for mailbox in mailboxes_to_search:
            try:
                # Select the mailbox
                status, _ = mail.select(mailbox, readonly=True) # Read-only mode is safer
                if status != 'OK':
                    print(f"Could not select mailbox '{mailbox}'. Skipping.")
                    continue

                # Search for all emails and get the latest 10
                status, data = mail.search(None, "ALL")
                if status != 'OK':
                    print(f"Could not search emails in '{mailbox}'. Skipping.")
                    continue

                mail_ids = data[0].split()
                # Get the last 10 emails from the current mailbox
                recent_mail_ids = mail_ids[-10:] if len(mail_ids) > 10 else mail_ids

                for num in recent_mail_ids:
                    status, msg_data = mail.fetch(num, "(RFC822)")
                    if status != 'OK':
                        print(f"Could not fetch email {num} from '{mailbox}'. Skipping.")
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Decode subject to handle different encodings
                    decoded_subject = ''
                    try:
                        decoded_headers = decode_header(msg.get("subject", ""))
                        for part, charset in decoded_headers:
                            if isinstance(part, bytes):
                                try:
                                    decoded_subject += part.decode(charset if charset else 'utf-8')
                                except (UnicodeDecodeError, TypeError):
                                    decoded_subject += part.decode('latin-1', errors='replace') # Fallback
                            else:
                                decoded_subject += part
                    except Exception as e:
                        print(f"Error decoding subject: {e}")
                        decoded_subject = msg.get("subject", "No Subject") # Fallback

                    # Clean up subject (e.g., remove newlines from decoding)
                    subject = re.sub(r'\s+', ' ', decoded_subject).strip()


                    content = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdisp = part.get('Content-Disposition')

                            # Only consider plain text parts and ignore attachments
                            if ctype == 'text/plain' and cdisp is None:
                                try:
                                    payload = part.get_payload(decode=True)
                                    charset = part.get_content_charset()
                                    if charset:
                                        content += payload.decode(charset, errors="ignore")
                                    else:
                                        content += payload.decode('utf-8', errors="ignore")
                                except Exception as e:
                                    print(f"Error decoding part content: {e}")
                                    content += "[Could not decode part content]" # Fallback
                    else:
                        try:
                            payload = msg.get_payload(decode=True)
                            charset = msg.get_content_charset()
                            if charset:
                                content = payload.decode(charset, errors="ignore")
                            else:
                                content = payload.decode('utf-8', errors="ignore")
                        except Exception as e:
                            print(f"Error decoding single part content: {e}")
                            content = "[Could not decode email content]" # Fallback

                    emails.append((subject, content))

            except Exception as e:
                print(f"Error processing mailbox '{mailbox}': {e}")
                # Continue to next mailbox if one fails

    except imaplib.IMAP4.error as e:
        print(f"IMAP login error: {e}")
        raise ValueError(f"Failed to log in to Gmail. Please check your email and App Password. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
    finally:
        if mail:
            try:
                mail.logout() # Ensure logout even if errors occur
            except Exception as e:
                print(f"Error during IMAP logout: {e}")

    return emails
