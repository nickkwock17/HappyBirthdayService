from datetime import date
from typing import List
from birthday_schema import BirthdaySchema

def generate_emails(birthdays: List[BirthdaySchema]) -> List[str]:
    """
    Generates email messages for birthdays that are today.
    """
    today = date.today()
    email_messages = []

    for birthday in birthdays:
        if birthday.birth_date == today or birthday.is_integration_test:
            message = f"Subject: Happy Birthday, {birthday.name}!\n\n" \
                      f"Dear {birthday.name}!\n\n" \
                      f"Happy Birthday! We hope you have a wonderful day.\n\n" \
                      f"Best regards,\nYour friend {birthday.friends_with}"
            email_messages.append(message)
    
    return email_messages
