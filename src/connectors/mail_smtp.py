#INFO: Send mail via SMTP

from util.cfg import CFG

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def prepare_email(sender, recipient, subject, text):
  message = MIMEMultipart()
  message['From'] = sender
  message['To'] = recipient
  message['Subject'] = subject
  message.attach(MIMEText(text, 'plain'))

  return message

def send_email(sender, recipient, message):
  session = smtplib.SMTP(*CFG.SMTP_host)
  session.starttls() #A: Enable security
  session.login(*CFG.SMTP_login)

  text = message.as_string()

  session.sendmail(sender, recipient, text)

def send_emails(text, recipients = CFG.Mail_recipients, subject = 'Finances Report'):
  for recipient in recipients:
    message = prepare_email(CFG.Mail_sender, recipient, subject, text)
    send_email(CFG.Mail_sender, recipient, message)

if __name__ == '__main__':
  send_emails('Testing', CFG.Mail_recipients)
