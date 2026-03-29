# HappyBirthdayService

An automated birthday reminder service that sends personalized emails to friends on their birthdays. Written by Nick and Havish.

## Features

- Automatically sends personalized birthday emails to friends on their birthday
- Runs fully automated every morning at 6am PT

## Roadmap

- **Multi-sender support** — Send emails from each friend's own account rather than a single shared account
- **Advance reminders** — Notify a list of people X days before a birthday
- **Separate integration test mode** — A dedicated daily trigger runs only integration-test-marked entries to verify the pipeline end-to-end
- **E2E test suite** — Runs on every pull request to master, verifying a real email is sent and received
- **Gift card sending** — Automatically send a gift card alongside the birthday email via the Giftbit API

## Stack

- Python 3.12 (AWS Lambda)
- Google Sheets (birthday data)
- AWS: Lambda, EventBridge Scheduler, Secrets Manager, IAM
- Terraform + GitHub Actions (CI/CD)
