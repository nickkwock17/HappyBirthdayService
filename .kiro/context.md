# HappyBirthdayService — Project Context

_Last updated: 2026-03-28_

## Overview
Automated birthday email reminder service. Written by Nick and Havish.
Reads birthday data from a Google Sheet and sends personalized emails to friends on their birthdays.

## Architecture

```
EventBridge Scheduler (6am PT)            → Lambda (mode=real)
EventBridge Scheduler (integration test)  → Lambda (mode=integration_test)
  → AWS Secrets Manager (Google Sheets + SMTP creds)
  → Google Sheets API
  → Gmail SMTP
```

## Key Files

| File | Purpose |
|---|---|
| `lambda/index.py` | Lambda handler entrypoint |
| `lambda/db.py` | Fetches birthday rows from Google Sheets (or mock data locally) |
| `lambda/email_generator.py` | Builds `Email` objects from birthday records |
| `lambda/email_service.py` | Sends emails via Gmail SMTP (prod) or logs to console (local) |
| `lambda/birthday_schema.py` | `BirthdaySchema` and `Email` dataclasses |
| `lambda/requirements.txt` | `gspread`, `google-auth` |
| `lambda/dependencies/` | Vendored pip packages (bundled into Lambda zip) |
| `terraform/main.tf` | All AWS infra (Lambda, IAM, EventBridge Scheduler) |
| `terraform/terraform.tfvars` | Prod variable values |
| `terraform/local.tfvars` | Local variable values |
| `.github/workflows/terraform.yml` | CI/CD: push to master → terraform apply |

## Data Model — `BirthdaySchema`
```python
name: str
email: str
birth_date: date
friends_with: str
remind_in_days: Optional[int] = None
is_integration_test: Optional[bool] = False
```

## Google Sheet Schema (sheet1)
Columns: `Name`, `Email`, `BirthDate` (YYYY-MM-DD), `FriendsWith`, `RemindInDays`, `IsIntegrationTest`

## AWS Infrastructure
- **Region**: us-west-2
- **Lambda**: `birthday-checker`, runtime python3.12, timeout 30s
- **Env vars on Lambda**: `ENV`, `GOOGLE_SHEETS_SECRET_NAME`, `GOOGLE_SHEET_ID`, `SMTP_SECRET_NAME`
- **Secrets Manager**: `google_sheets_credentials` (Google service account JSON), `smtp_credentials` (keys: `email`, `password`)
- **Scheduler**: `birthday-check-schedule` — `cron(0 6 * * ? *)` America/Los_Angeles
- **Terraform state**: stored in repo (`terraform/terraform.tfstate`), committed back by CI bot

## CI/CD (GitHub Actions)
- Trigger: push to `master`
- Auth to AWS: OIDC → IAM role `GitHubActions`
- Secrets needed: `AWS_ACCOUNT_ID`, `AWS_REGION`, `STATE_COMMIT_TOKEN`

---

## ✅ Done
- Birthday emails sent via Gmail SMTP on the birthday date
- SMTP + Google Sheets credentials fetched from AWS Secrets Manager
- `Email` dataclass — clean separation between generation and sending
- Lambda runs daily at 6am PT via EventBridge Scheduler
- Terraform-managed infra, auto-deployed via GitHub Actions on push to master

## ❌ Not Done Yet
1. **Separate integration test trigger** — Lambda should accept a `mode` parameter (`real` vs `integration_test`). Integration test mode only processes `is_integration_test=True` rows. Needs a second EventBridge Scheduler rule dedicated to this mode.
2. **E2E test on PR** — GitHub Actions workflow that invokes the Lambda in integration test mode and verifies an email was actually received. Inbox polling via IMAP or Gmail API (TBD).
3. **Multi-sender support** — All emails go through one Gmail account. Should route per sender based on `friends_with`. Requires per-sender SMTP credentials in Secrets Manager.
4. **Advance reminders** — `remind_in_days` is fetched but unused. Needs a new `remind_emails` field (list of emails to notify). Logic: send reminder when `today + remind_in_days == birth_date`.
5. **Gift card sending** — Integrate Giftbit API to send a gift card with birthday emails. API key in Secrets Manager. Decisions needed: amount, currency, which birthdays qualify.

---

## Local Dev
```bash
cd lambda && python test.py  # uses mock data, prints emails to console
```

## Notes
- `lambda/dependencies/` is vendored — added to `sys.path` in `index.py`
- Terraform zip built automatically via `archive_file` data source — no manual zip step
