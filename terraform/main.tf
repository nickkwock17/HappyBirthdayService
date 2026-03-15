provider "aws" {
  region = "us-west-2"
}

# 1. Archive the Lambda function code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/index.py"
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

# 4. Lambda Function
resource "aws_lambda_function" "birthday_checker" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "birthday-checker"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "index.handler"
  runtime          = "python3.12"
}

# 5. EventBridge Rule (Runs at 6:30 AM and 1:30 PM Pacific Time / 13:30 and 20:30 UTC)
resource "aws_cloudwatch_event_rule" "twice_daily_birthday_check" {
  name                = "twice-daily-birthday-check"
  description         = "Triggers birthday check Lambda at 6:30 AM and 1:30 PM Pacific Time"
  schedule_expression = "cron(30 13,20 * * ? *)"
}

# 6. EventBridge Target
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.twice_daily_birthday_check.name
  target_id = "BirthdayCheckLambda"
  arn       = aws_lambda_function.birthday_checker.arn
}

# 7. Lambda Permission (Allow EventBridge to invoke Lambda)
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.birthday_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.twice_daily_birthday_check.arn
}

output "lambda_arn" {
  value = aws_lambda_function.birthday_checker.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.birthday_checker.function_name
}
