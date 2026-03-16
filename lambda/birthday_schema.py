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

