# HappyBirthdayService

An automated birthday reminder service that sends personalized emails to friends on their birthdays. Written by Nick and Havish.

## Features

- Automatically sends personalized birthday emails to friends on their birthday
- Supports advance reminders — notify people X days before a birthday so they have time to prepare
- Runs fully automated every morning at 6am PT

## Roadmap

- **Multi-sender support** — Send emails from each friend's own account rather than a single shared account
- **Advance reminders** — Notify a list of people X days before a birthday
- **Gift card sending** — Automatically send a gift card alongside the birthday email via the Giftbit API

## Stack

- Python 3.12 (AWS Lambda)
- Google Sheets (birthday data)
- AWS: Lambda, EventBridge Scheduler, Secrets Manager, IAM
- Terraform + GitHub Actions (CI/CD)
