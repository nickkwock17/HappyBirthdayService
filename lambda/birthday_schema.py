from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class BirthdaySchema:
    name: str
    email: str
    birth_date: date
    friends_with: str
    remind_in_days: Optional[int] = None
    is_integration_test: Optional[bool] = False

@dataclass
class Email:
    to: str
    subject: str
    body: str

