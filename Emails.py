import imaplib
import email
from email.header import decode_header
import os
from Image import Generator
import cv2

def get_recent_email(folder_name="Inbox"):  # Default to "Inbox", but can be changed
    # Your Gmail credentials
    email_user = 'parameshbadiger26@gmail.com'
    email_pass = 'sydi ovdk tmoz qalv'

    # Connect to Gmail's IMAP server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login to your account
    mail.login(email_user, email_pass)

    # Select the mailbox you want to access
    mail.select(folder_name)  # Use the provided folder_name

    # Search for all emails in the mailbox
    status, messages = mail.search(None, "ALL")
    message_ids = messages[0].split()

    if message_ids:
        rows = []
        if len(message_ids) > 11:
            message_ids = message_ids[-10:]
        else:
            message_ids=message_ids
        
        print(len(message_ids))

        for email_id in message_ids:
            row = []
            # Fetch the email by ID
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]

            # Parse the raw email using the email library
            msg = email.message_from_bytes(raw_email)

            # Print the subject and sender
            subject, encoding = decode_header(msg["Subject"])[0]
            sender, encoding = decode_header(msg.get("From"))[0]
            row.append(sender)
            row.append(subject)
            # Print the body of the email and handle attachments
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Handle text parts
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        text = part.get_payload(decode=True).decode("utf-8")
                        text = text.strip()
                        if text:
                            row.append(text)
                    # Print or save images, videos, audios, PDFs, etc.
                    elif content_type in ["image/png", "image/jpeg"]:
                        filename = part.get_filename()
                        if filename:
                            # Save the attachment to a file
                            filepath = os.path.join(os.getcwd(), filename)
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            cap = Generator(filepath)
                            row.append(cap)
                rows.append(row) 
        else:
            print("No messages found.")

        mail.logout()
    return rows
