import imaplib
import email
from email.header import decode_header
import os
from Image import Generator
import cv2
import pytesseract
import pygame
import time
from gtts import gTTS
from mutagen.mp3 import MP3
import time
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

def text_to_speech(text1):
    print(text1)
    myobj = gTTS(text=text1, lang='en-us', tld='com', slow=False)
    myobj.save("voice.mp3")
    song = MP3("voice.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load('voice.mp3')
    pygame.mixer.music.play()
    time.sleep(song.info.length)
    pygame.quit()

def get_recent_email(folder_name="Inbox"):  # Default to "Inbox", but can be changed
    # Your Gmail credentials
    email_user = 'jyothika.cse.rymec@gmail.com'
    email_pass = 'nwky vicw mbca qbps'

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
        # Get the most recent email (last message ID)
        latest_email_id = message_ids[-1]

        # Fetch the email by ID
        _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        # Parse the raw email using the email library
        msg = email.message_from_bytes(raw_email)

        # Print the subject and sender
        subject, encoding = decode_header(msg["Subject"])[0]
        sender, encoding = decode_header(msg.get("From"))[0]
        print(f"Subject: {subject}")
        print(f"From: {sender}")

        text_to_speech("Email from "+sender)

        # Print the body of the email and handle attachments
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Handle text parts
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    text = part.get_payload(decode=True).decode("utf-8")
                    text = text.strip()
                    print(text)
                    if text:
                        text_to_speech("message is : "+part.get_payload(decode=True).decode("utf-8"))

                # Print or save images, videos, audios, PDFs, etc.
                elif content_type in ["image/png", "image/jpeg"]:
                    filename = part.get_filename()
                    if filename:
                        # Save the attachment to a file
                        filepath = os.path.join(os.getcwd(), filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Attachment saved: {filepath}")

                        # Read image from which text needs to be extracted
                        img = cv2.imread(filepath)
                        # Convert the image to gray scale
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        text1 = pytesseract.image_to_string(gray)
                        text1 = text1.strip()
                        if text1:
                            text_to_speech("message is : "+text1)
                        else:
                            cap = Generator(filepath)
                            print('caption ', cap)
                            text_to_speech("caption is : "+cap)
        else:
            print(msg.get_payload(decode=True).decode("utf-8"))

        print("-" * 50)

    else:
        print("No messages found.")

    mail.logout()
