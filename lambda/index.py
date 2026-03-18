import os
import sys

# Add local dependencies folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies"))

from email_service import send_emails
from db import get_all_birthday_rows_from_database
from email_generator import generate_emails


def handler(event, context):
    print("Checking for upcoming birthdays...")

    env = os.getenv("ENV")
    print(f"Running in environment: {env}")

    birthdays = get_all_birthday_rows_from_database(env)
    email_messages = generate_emails(birthdays)

    if email_messages:
        print(f"Generated {len(email_messages)} email(s).")
        send_emails(env, email_messages)
    else:
        print("No emails to send today.")

    return {
        'statusCode': 200,
        'body': 'Successfully checked birthdays!'
    }


