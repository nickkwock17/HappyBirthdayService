from typing import List

def send_emails(env: str, messages: List[str]):
    """
    Sends emails. For 'local' env, it prints messages to the console.
    For 'prod', it's intended to send emails using a real email service.
    """
    if env == 'prod':
        # TODO: Implement the logic to send emails using SMTP and AWS Secrets Manager
        print("Running in 'prod' environment. Email sending not yet implemented.")
        return
    else:
        return log_mock_emails(messages)

def log_mock_emails(messages: List[str]):
    """Helper function to print email content for local testing."""
    print("Running in 'local' environment, logging emails instead of sending.")
    if not messages:
        print("No emails to send.")
        return
    
    print("--- MOCK EMAIL START ---")
    for i, message in enumerate(messages):
        print(f"Email {i+1}:")
        print(message)
        print("-" * 10)
    print("--- MOCK EMAIL END ---")