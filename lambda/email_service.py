import os
import json
import boto3
import smtplib
from email.mime.text import MIMEText
from typing import List
from birthday_schema import Email


def get_smtp_credentials():
    secret_name = os.getenv("SMTP_SECRET_NAME")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def send_emails(env: str, emails: List[Email]):
    if env == 'prod':
        creds = get_smtp_credentials()
        smtp_email = creds["email"]
        smtp_password = creds["password"]

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            for email in emails:
                msg = MIMEText(email.body)
                msg["Subject"] = email.subject
                msg["From"] = smtp_email
                msg["To"] = email.to
                server.sendmail(smtp_email, email.to, msg.as_string())
                print(f"Sent email to {email.to}: {email.subject}")
    else:
        log_mock_emails(emails)


def log_mock_emails(emails: List[Email]):
    print("Running in 'local' environment, logging emails instead of sending.")
    if not emails:
        print("No emails to send.")
        return
    print("--- MOCK EMAIL START ---")
    for i, email in enumerate(emails):
        print(f"Email {i+1}: To={email.to} | Subject={email.subject}")
        print(email.body)
        print("-" * 10)
    print("--- MOCK EMAIL END ---")
