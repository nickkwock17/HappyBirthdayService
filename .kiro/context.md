# HappyBirthdayService — Project Context

_Last updated: 2026-03-28_

## Overview
Automated birthday email reminder service. Written by Nick and Havish.
- Reads birthday data from a Google Sheet
- Sends reminder emails to friends on (or before) birthdays
- Runs on AWS Lambda, triggered twice daily via EventBridge Scheduler

## Architecture

```
EventBridge Scheduler (6am + 2pm PT daily)
  → Lambda (birthday-checker, Python 3.12)
      → AWS Secrets Manager (Google Sheets service account creds)
      → Google Sheets API (birthday data source)
      → Email sending (TODO: not yet implemented for prod)
```

## Key Files

| File | Purpose |
|---|---|
| `lambda/index.py` | Lambda handler entrypoint |
| `lambda/db.py` | Fetches birthday rows from Google Sheets (or mock data locally) |
| `lambda/email_generator.py` | Generates email message strings from birthday records |
| `lambda/email_service.py` | Sends emails (prod: **TODO/stub**; local: prints to console) |
| `lambda/birthday_schema.py` | `BirthdaySchema` dataclass |
| `lambda/requirements.txt` | `gspread`, `google-auth` |
| `lambda/dependencies/` | Vendored pip packages (bundled into Lambda zip) |
| `terraform/main.tf` | All AWS infra (Lambda, IAM, EventBridge Scheduler) |
| `terraform/terraform.tfvars` | Prod variable values (env=prod, Google Sheet ID) |
| `terraform/local.tfvars` | Local variable values (env=local) |
| `.github/workflows/terraform.yml` | CI/CD: push to master → terraform apply |

## Data Model — `BirthdaySchema`
```python
name: str
email: str
birth_date: date
friends_with: str
remind_in_days: Optional[int] = None   # not yet used in logic
is_integration_test: Optional[bool] = False  # bypasses date check
```

## Google Sheet Schema (sheet1)
Columns: `Name`, `Email`, `BirthDate` (YYYY-MM-DD), `FriendsWith`, `RemindInDays`, `IsIntegrationTest`

## AWS Infrastructure
- **Region**: us-west-2
- **Lambda**: `birthday-checker`, runtime python3.12, timeout 30s
- **Env vars on Lambda**: `ENV`, `GOOGLE_SHEETS_SECRET_NAME`, `GOOGLE_SHEET_ID`, `SMTP_SECRET_NAME`
- **Secrets Manager**: `google_sheets_credentials` (Google service account JSON), `smtp_credentials` (keys: `email`, `password`)
- **Scheduler**: `birthday-check-schedule` — `cron(0 6 * * ? *)` in America/Los_Angeles (6am PT only)
- **Terraform state**: stored in repo (`terraform/terraform.tfstate`), committed back by CI bot

## CI/CD (GitHub Actions)
- Trigger: push to `master`
- Auth to AWS: OIDC → IAM role `GitHubActions` (account ID from secret `AWS_ACCOUNT_ID`)
- Steps: checkout → configure AWS → terraform init → fmt check → plan → apply → commit state
- Secrets needed: `AWS_ACCOUNT_ID`, `AWS_REGION`, `STATE_COMMIT_TOKEN`

## Known TODOs / Incomplete Work
1. ~~**Email sending in prod is not implemented**~~ — Implemented via SMTP (Gmail, port 465). Creds fetched from Secrets Manager secret `smtp_credentials` (keys: `email`, `password`).
2. **Multi-sender support** — All emails currently go through one Gmail account. Should route per sender: Nick's emails via Nick's account, Havish's via Havish's. Requires per-sender SMTP credentials in Secrets Manager and routing logic on `friends_with`.
3. **Remind-in-days feature incomplete** — `remind_in_days` is fetched but unused. Needs a new `remind_emails` field (single or list of emails to notify in advance). `email_generator.py` needs logic: `today + remind_in_days == birth_date`.
4. **Giftcard sending** — Integrate Giftbit API to send a gift card with birthday emails. API key in Secrets Manager. Decisions needed: gift amount, currency, which birthdays qualify.
5. **`local.tfvars` is gitignored** (partially — `*.tfvars` is commented out in `.gitignore`, so tfvars ARE committed). The `local.tfvars` only sets `environment = "local"`.

## Local Dev
```bash
# Run lambda locally (uses mock data, prints emails to console)
cd lambda
python test.py
```

## Notes
- The `lambda/dependencies/` folder is vendored (not installed at runtime) — added to `sys.path` in `index.py`
- `is_integration_test=True` rows bypass the date check and always generate an email (useful for smoke testing prod)
- Terraform zip is built by terraform itself via `archive_file` data source — no manual zip step needed
