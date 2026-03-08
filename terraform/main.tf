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

output "lambda_arn" {
  value = aws_lambda_function.birthday_checker.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.birthday_checker.function_name
}
