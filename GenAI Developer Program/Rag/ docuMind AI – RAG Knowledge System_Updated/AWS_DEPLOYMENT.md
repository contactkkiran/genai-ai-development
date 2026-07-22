# AWS Deployment Guide for DocuMind AI

## Overview

This guide explains how to deploy DocuMind AI to AWS using multiple deployment options.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed (for local testing)
- Git for version control

---

## Option 1: AWS ECS Fargate (Recommended)

### Step 1: Create ECR Repository

```bash
# Create AWS ECR repository
aws ecr create-repository --repository-name documind-ai --region us-east-1

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Docker Image

```bash
# Build Docker image
docker build -t documind-ai:latest .

# Tag image for ECR
docker tag documind-ai:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest
```

### Step 3: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "documind-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "documind-api",
      "image": "<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "info"
        },
        {
          "name": "WORKERS",
          "value": "4"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:documind/openai-api-key:OPENAI_API_KEY::"
        },
        {
          "name": "API_KEY_SECRET",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:documind/api-key:API_KEY_SECRET::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/documind-ai",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole"
}
```

### Step 4: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name documind-cluster --region us-east-1

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region us-east-1

# Create service
aws ecs create-service \
  --cluster documind-cluster \
  --service-name documind-service \
  --task-definition documind-ai \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=documind-api,containerPort=8000 \
  --region us-east-1
```

---

## Option 2: AWS Elastic Beanstalk

### Step 1: Create Elastic Beanstalk Application

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker documind-ai --region us-east-1

# Create environment
eb create documind-env --instance-type t3.medium --scale 2
```

### Step 2: Deploy

```bash
# Deploy application
eb deploy

# View logs
eb logs

# Monitor environment
eb status
```

---

## Option 3: AWS Lambda + API Gateway

### Step 1: Create Lambda Function

```bash
# Install serverless framework (optional)
npm install -g serverless

# Create serverless.yml for DocuMind AI
# Use Mangum as ASGI adapter for Lambda
```

**serverless.yml:**

```yaml
service: documind-ai

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${ssm:/documind/openai-api-key}
    ENVIRONMENT: production

functions:
  api:
    handler: app.main.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    environment:
      PYTHONPATH: /var/task

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
```

### Step 2: Deploy to Lambda

```bash
serverless deploy
```

---

## Environment Setup

### Step 1: Store Secrets in AWS Secrets Manager

```bash
# Store OpenAI API Key
aws secretsmanager create-secret \
  --name documind/openai-api-key \
  --secret-string '{"OPENAI_API_KEY":"your-key-here"}' \
  --region us-east-1

# Store API Key
aws secretsmanager create-secret \
  --name documind/api-key \
  --secret-string '{"API_KEY_SECRET":"your-secret-here"}' \
  --region us-east-1
```

### Step 2: Create CloudWatch Log Group

```bash
aws logs create-log-group --log-group-name /ecs/documind-ai --region us-east-1

aws logs put-retention-policy \
  --log-group-name /ecs/documind-ai \
  --retention-in-days 30 \
  --region us-east-1
```

---

## Database: S3 + EBS for Persistence

### Step 1: Create S3 Bucket for Vector Database

```bash
# Create S3 bucket
aws s3 mb s3://documind-ai-db --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket documind-ai-db \
  --versioning-configuration Status=Enabled

# Add encryption
aws s3api put-bucket-encryption \
  --bucket documind-ai-db \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
```

### Step 2: Configure S3 Sync

Add to your deployment script:

```bash
# Backup DB before deployment
aws s3 sync ./data/db s3://documind-ai-db/backups/$(date +%Y%m%d-%H%M%S)/

# Download DB on startup
aws s3 sync s3://documind-ai-db/latest/ ./data/db/

# Upload DB after ingest
aws s3 sync ./data/db s3://documind-ai-db/latest/
```

---

## Monitoring & Logging

### Step 1: CloudWatch Metrics

```bash
# View logs
aws logs tail /ecs/documind-ai --follow

# Create custom metric
aws cloudwatch put-metric-alarm \
  --alarm-name documind-error-rate \
  --alarm-description "Alert on high error rate" \
  --metric-name Errors \
  --namespace ECS/ContainerInsights \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Step 2: Enable X-Ray Tracing

Add to FastAPI app:

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

xray_recorder.configure(service='DocuMind AI')
```

### Step 3: Sentry Integration

```bash
# Create Sentry project and get DSN
# Add to environment
export SENTRY_DSN="https://key@sentry.io/project-id"
```

---

## Load Balancing & Auto-Scaling

### Step 1: Create Application Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
  --name documind-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --matcher HttpCode=200

# Create load balancer
aws elbv2 create-load-balancer \
  --name documind-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing
```

### Step 2: Auto Scaling Policy

```bash
# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name documind-asg \
  --launch-template LaunchTemplateName=documind,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --availability-zones us-east-1a us-east-1b

# Create scaling policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name documind-asg \
  --policy-name documind-scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://scaling-config.json
```

---

## CI/CD Pipeline with AWS CodePipeline

### Step 1: Create CodeBuild Project

**buildspec.yml:**

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo "Logging into ECR..."
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/documind-ai
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}

  build:
    commands:
      - echo "Building Docker image..."
      - docker build -t $REPOSITORY_URI:$IMAGE_TAG .
      - docker tag $REPOSITORY_URI:$IMAGE_TAG $REPOSITORY_URI:latest

  post_build:
    commands:
      - echo "Pushing Docker image to ECR..."
      - docker push $REPOSITORY_URI:$IMAGE_TAG
      - docker push $REPOSITORY_URI:latest
      - echo "Writing image definitions file..."
      - printf '[{"name":"documind-api","imageUri":"%s"}]' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files: imagedefinitions.json
```

---

## Cost Optimization Tips

1. **Use Fargate Spot** for non-critical workloads (70% savings)
2. **Enable S3 Intelligent Tiering** for database backups
3. **Use CloudFront** for API caching
4. **Right-size instances** based on performance metrics
5. **Use Reserved Instances** for baseline capacity

---

## Security Best Practices

1. ✅ Use AWS Secrets Manager for sensitive data
2. ✅ Enable VPC endpoints for private connectivity
3. ✅ Use Security Groups restrictively
4. ✅ Enable VPC Flow Logs for traffic monitoring
5. ✅ Use KMS for encryption at rest
6. ✅ Enable WAF for API protection
7. ✅ Regularly rotate API keys
8. ✅ Enable CloudTrail for audit logging

---

## Disaster Recovery

### Backup Strategy

```bash
# Daily backup to S3
0 2 * * * aws s3 sync /data/db s3://documind-ai-db/backups/$(date +\%Y\%m\%d)/

# Cleanup old backups (keep 30 days)
aws s3 sync s3://documind-ai-db/backups/ s3://documind-ai-db/backups/ \
  --delete \
  --exclude "*" \
  --include "202301*" \
  --include "202302*"
```

### Recovery Procedure

```bash
# Restore from backup
aws s3 sync s3://documind-ai-db/backups/20240115/ /data/db/

# Restart ECS service
aws ecs update-service \
  --cluster documind-cluster \
  --service documind-service \
  --force-new-deployment
```

---

## Cost Estimation (Monthly)

| Component         | Config                | Cost               |
| ----------------- | --------------------- | ------------------ |
| **Fargate**       | 2 x 1GB, 10GB storage | ~$30               |
| **ALB**           | 1 ALB, 0.5M req/mo    | ~$25               |
| **RDS/Aurora**    | (if used)             | $50+               |
| **S3**            | 10GB storage, 1M ops  | ~$2                |
| **CloudWatch**    | Logs, metrics         | ~$5                |
| **Data Transfer** | 10GB out/mo           | ~$1                |
| **Total**         | Minimum setup         | **~$60-100/month** |

---

## Troubleshooting

### Task Won't Start

- Check CloudWatch logs: `aws logs tail /ecs/documind-ai --follow`
- Verify IAM role permissions
- Check container image in ECR

### High Latency

- Check Task CPU/Memory
- Monitor OpenAI API response times
- Enable CloudFront caching

### Database Issues

- Verify S3 bucket permissions
- Check disk space on ECS instance
- Monitor ChromaDB performance

---

## Next Steps

1. Set up monitoring dashboard
2. Create auto-scaling policies
3. Implement backup automation
4. Set up CI/CD pipeline
5. Configure CDN caching
6. Implement rate limiting at ALB level
7. Set up incident alerting
8. Plan for disaster recovery drills
