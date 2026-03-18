import os
import json
import boto3
import gspread
from datetime import date, datetime
from typing import List
from birthday_schema import BirthdaySchema
from google.oauth2.service_account import Credentials

def get_secret(secret_name: str):
    """Retrieves the secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

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

def retrieve_rows_from_google_sheets() -> List[BirthdaySchema]:
    print("Fetching data from Google Sheets...")
    
    secret_name = os.getenv("GOOGLE_SHEETS_SECRET_NAME")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    
    if not secret_name or not sheet_id:
        print("Error: GOOGLE_SHEETS_SECRET_NAME or GOOGLE_SHEET_ID not set.")
        return []

    try:
        # 1. Get credentials from Secrets Manager
        creds_json = get_secret(secret_name)
        
        # 2. Authenticate with Google
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        gc = gspread.authorize(creds)
        
        # 3. Open the sheet and get all records
        sheet = gc.open_by_key(sheet_id).sheet1
        rows = sheet.get_all_records()
        
        # 4. Map rows to BirthdaySchema
        birthdays = []
        for row in rows:
            # Assumes column names: Name, Email, BirthDate, FriendsWith, RemindInDays
            # Date format assumed to be YYYY-MM-DD
            birth_date_str = row.get("BirthDate")
            if birth_date_str:
                birth_date = datetime.strptime(str(birth_date_str), "%Y-%m-%d").date()
            else:
                continue

            birthdays.append(BirthdaySchema(
                name=row.get("Name"),
                email=row.get("Email"),
                birth_date=birth_date,
                friends_with=row.get("FriendsWith"),
                remind_in_days=int(row.get("RemindInDays")) if row.get("RemindInDays") else None
            ))
        
        return birthdays

    except Exception as e:
        print(f"Error retrieving rows from Google Sheets: {e}")
        return []

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