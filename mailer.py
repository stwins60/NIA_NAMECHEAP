import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv('EMAIL')
SERVER = os.getenv('SERVER')
SERVER_PASS = os.getenv('SERVER_PASS')
PORT = os.getenv('PORT')

def sendMyEmail(subject, msg, phone_num, name="nia-pro", email="tdairo16@gmail.com"):
    try:
        server = smtplib.SMTP_SSL(SERVER, PORT)
        server.ehlo()
        server.login(USERNAME, SERVER_PASS)
        print('Connected to server')
        sender_email = "support@nigeriaislamicassociation.org"
        receiver_email = 'tdairo16@gmail.com'
        # receiver_email = 'idrisniyi94@gmail.com'
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">

            <p style="font-size: 16px;">
                Assalamu Alaikum NIA,
            </p>

            <p style="font-size: 16px;">
                This message was sent from:
            </p>

            <ul style="list-style-type: none; padding: 0;">
                <li style="font-size: 16px;"><strong>User Name:</strong> {name}</li>
                <li style="font-size: 16px;"><strong>Email:</strong> {email}</li>
                <li style="font-size: 16px;"><strong>Phone Number:</strong> {phone_num}</li>
            </ul>

            <p style="font-size: 16px;"><strong>Message Content:</strong></p>

            <div style="font-size: 16px;">
               {msg}
            </div>

            <p style="font-size: 16px;">
                Jazakallah Khair,
                <br>{name}
                <br>{email}
                <br>{phone_num}
            </p>

        </body>
        </html>
        """
        part = MIMEText(html, 'html')
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = receiver_email
        message.attach(part)

        # message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(sender_email, receiver_email, subject, msg)
        # message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(sender_email, receiver_email, 'Test', 'This is a test email')
        server.sendmail(sender_email, receiver_email, message.as_string())
        print('Email sent successfully')
    except Exception as e:
        print(e)
        print('Failed to connect to server')

# sendMyEmail('Test', 'This is a test email', '312-838-1977', "Idris", 'idrisniyi94@gmail.com')