from datetime import date, timedelta
from typing import List
from birthday_schema import BirthdaySchema

def get_all_birthday_rows_from_database(env: str) -> List[BirthdaySchema]:
    """
    Retrieves birthday records. For 'local' env, it returns mock data.
    For 'prod', it's intended to fetch from a real database.
    """
    if env == 'prod':
        return retrieve_rows_from_google_sheets()
    else:
        print(f"Unknown environment: {env}. Running locally.")
        return generate_test_rows()

def retrieve_rows_from_google_sheets():
    print("Running in 'prod' environment. Database logic not yet implemented.")
    # TODO: Implement the logic to fetch data from the production database


def generate_test_rows():
    print("Running in 'local' environment, returning mock data.")
    # For local testing, return a predefined list of BirthdaySchema objects
    today = date.today()
    return [
        BirthdaySchema(
            name="Havish Maka",
            email="havish747@gmail.com",
            birth_date=today,
            friends_with="Nick"
        ),
        BirthdaySchema(
            name="Nick Kwock",
            email="happybirthdayfromnick@gmail.com",
            birth_date=today,
            friends_with="Havish",
            remind_in_days=5
        ),
    ]