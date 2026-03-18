variable "environment" {
  description = "The deployment environment (e.g., 'local', 'prod')."
  type        = string
  default     = "local"
}

variable "google_sheet_id" {
  description = "The ID of the Google Sheet containing birthday data."
  type        = string
  default     = "REPLACE_WITH_YOUR_SHEET_ID"
}

provider "aws" {
  region = "us-west-2"
}

# 1. Archive the Lambda function code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/"
  output_path = "${path.module}/lambda_function_payload.zip"
}

# 2. IAM Role for Lambda execution
resource "aws_iam_role" "lambda_exec_role" {
  name = "birthday_checker_lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# 3. Attach basic logging policy to the role
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3a. Attach policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_secrets" {
  name = "birthday_checker_lambda_secrets_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "secretsmanager:GetSecretValue"
        Effect   = "Allow"
        Resource = aws_secretsmanager_secret.google_sheets_creds.arn
      }
    ]
  })
}

# 3b. Secrets Manager Secret
resource "aws_secretsmanager_secret" "google_sheets_creds" {
  name        = "google_sheets_credentials"
  description = "Google Service Account JSON credentials for birthday sheet"
}

# 4. Lambda Function
resource "aws_lambda_function" "birthday_checker" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "birthday-checker"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "index.handler"
  runtime          = "python3.12"

  environment {
    variables = {
      ENV                       = var.environment
      GOOGLE_SHEETS_SECRET_NAME = aws_secretsmanager_secret.google_sheets_creds.name
      GOOGLE_SHEET_ID           = var.google_sheet_id
    }
  }
}

# 5. IAM Role for EventBridge Scheduler
resource "aws_iam_role" "scheduler_role" {
  name = "birthday_checker_scheduler_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

# 6. Policy to allow Scheduler to invoke Lambda
resource "aws_iam_role_policy" "scheduler_policy" {
  name = "birthday_checker_scheduler_policy"
  role = aws_iam_role.scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.birthday_checker.arn
      }
    ]
  })
}

# 7. EventBridge Scheduler Schedule (Native Pacific Time support)
resource "aws_scheduler_schedule" "birthday_check_schedule" {
  name       = "birthday-check-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 6,14 * * ? *)"
  schedule_expression_timezone = "America/Los_Angeles"

  target {
    arn      = aws_lambda_function.birthday_checker.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

output "lambda_arn" {
  value = aws_lambda_function.birthday_checker.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.birthday_checker.function_name
}
