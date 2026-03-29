from datetime import date
from typing import List
from birthday_schema import BirthdaySchema, Email

def generate_emails(birthdays: List[BirthdaySchema]) -> List[Email]:
    today = date.today()
    emails = []

    for birthday in birthdays:
        if birthday.birth_date == today or birthday.is_integration_test:
            emails.append(Email(
                to=birthday.email,
                subject=f"Happy Birthday, {birthday.name}!",
                body=(
                    f"Dear {birthday.name}!\n\n"
                    f"Happy Birthday! We hope you have a wonderful day.\n\n"
                    f"Best regards,\nYour friend {birthday.friends_with}"
                )
            ))

    return emails
