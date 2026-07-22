# Production Deployment Guide

## Quick Start for Production

### 1. Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with production values
nano .env

# Required variables for production:
# - OPENAI_API_KEY=your_key
# - API_KEY_SECRET=your_secret
# - ENVIRONMENT=production
# - DEBUG=false
```

### 2. Local Testing with Docker

```bash
# Build image
docker build -t documind-ai:latest .

# Run locally with docker-compose
docker-compose up

# Test endpoint
curl -X POST http://localhost:8000/query?q="Test%20query" \
  -H "x-api-key: your_api_key" \
  -H "x-client-id: test-client"

# Check health
curl http://localhost:8000/health
```

### 3. AWS Deployment

**Option A: Using ECS Fargate (Recommended)**

```bash
# See AWS_DEPLOYMENT.md for detailed instructions
aws ecr create-repository --repository-name documind-ai
docker build -t documind-ai:latest .
docker tag documind-ai:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest
```

**Option B: Using Elastic Beanstalk**

```bash
eb init -p docker documind-ai
eb create documind-env
eb deploy
```

**Option C: Using Lambda + API Gateway**

```bash
serverless deploy
```

---

## Configuration Reference

### Critical Environment Variables

| Variable                | Value        | Notes                                      |
| ----------------------- | ------------ | ------------------------------------------ |
| `ENVIRONMENT`           | `production` | Must be "production" for security features |
| `DEBUG`                 | `false`      | Disables debug endpoints                   |
| `LOG_LEVEL`             | `info`       | Can be: debug, info, warning, error        |
| `OPENAI_API_KEY`        | _secret_     | Store in AWS Secrets Manager               |
| `API_KEY_SECRET`        | _secret_     | Store in AWS Secrets Manager               |
| `RATE_LIMIT_PER_MINUTE` | `60`         | Adjust based on usage                      |
| `WORKERS`               | `4`          | CPUs available / number of workers         |

### Derived Configuration

```
CHROMA_DB_PATH=data/db           # Vector database location
CACHE_ENABLED=true               # Enable response caching
CACHE_TTL_SECONDS=3600           # Cache 1 hour
REQUEST_TIMEOUT=30               # API request timeout
OPENAI_TIMEOUT=60                # LLM API timeout
```

---

## API Authentication

### Production Security

All endpoints except `/health` require authentication in production:

```bash
# Required header for /ingest
curl -X POST http://localhost:8000/ingest \
  -H "x-api-key: YOUR_API_KEY_SECRET"

# Required header for /query
curl -X POST "http://localhost:8000/query?q=your%20question" \
  -H "x-api-key: YOUR_API_KEY_SECRET" \
  -H "x-client-id: client-name"
```

### Generate API Keys

```bash
# Create a strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name documind/api-key \
  --secret-string '{"API_KEY_SECRET":"<GENERATED_KEY>"}'
```

---

## Monitoring & Alerting

### CloudWatch Metrics

Monitor these key metrics:

- **API Latency** (p50, p95, p99)
- **Error Rate** (errors / total requests)
- **Request Count** (per minute)
- **Task CPU & Memory**
- **Database Size**

### Create Alarms

```bash
# High error rate alert
aws cloudwatch put-metric-alarm \
  --alarm-name documind-high-errors \
  --alarm-description "Alert when error rate > 5%" \
  --metric-name ErrorRate \
  --namespace DocumentMind \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold

# High latency alert
aws cloudwatch put-metric-alarm \
  --alarm-name documind-high-latency \
  --alarm-description "Alert when p95 latency > 2s" \
  --metric-name Latency \
  --namespace DocumentMind \
  --statistic Average \
  --period 60 \
  --threshold 2000 \
  --comparison-operator GreaterThanThreshold
```

### View Logs

```bash
# Real-time logs
aws logs tail /ecs/documind-ai --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/documind-ai \
  --filter-pattern "ERROR"

# Get metrics
aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name CPUUtilized \
  --dimensions Name=ServiceName,Value=documind-service \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-16T00:00:00Z \
  --period 300 \
  --statistics Average
```

---

## Logging & Debugging

### Log Levels

- **DEBUG**: Development only, verbose output
- **INFO**: Production logs, key events
- **WARNING**: Potential issues
- **ERROR**: Critical problems

### JSON Logging

Production uses JSON format for structured logging:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "Processing query",
  "module": "main",
  "function": "query",
  "line": 145,
  "request_id": "abc-123",
  "client_id": "prod-client"
}
```

### Common Issues

**Issue: "Internal Server Error"**

```bash
# Check recent errors
aws logs filter-log-events \
  --log-group-name /ecs/documind-ai \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000
```

**Issue: "Rate limit exceeded"**

```bash
# Increase rate limit
export RATE_LIMIT_PER_MINUTE=120

# Or implement API Gateway throttling
aws apigateway update-stage \
  --rest-api-id api-id \
  --stage-name prod \
  --patch-operations op=replace,path=/*\/throttle/rateLimit,value=1000
```

**Issue: "Timeout"**

```bash
# Increase timeout and check OpenAI API
export REQUEST_TIMEOUT=60
export OPENAI_TIMEOUT=120

# Check OpenAI status
curl https://status.openai.com/
```

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# Daily backup at 2 AM UTC
0 2 * * * aws s3 sync /data/db s3://documind-ai-db/daily/$(date +\%Y\%m\%d)/

# Retain last 30 days
aws s3 sync s3://documind-ai-db/ s3://documind-ai-db/ \
  --delete \
  --exclude "daily/2023*"
```

### Restore from Backup

```bash
# List available backups
aws s3 ls s3://documind-ai-db/daily/

# Restore specific backup
aws s3 sync s3://documind-ai-db/daily/20240115/ /data/db/

# Restart service
aws ecs update-service \
  --cluster documind-cluster \
  --service documind-service \
  --force-new-deployment
```

---

## Performance Tuning

### Database Optimization

```python
# In retriever.py, adjust chunk count
search_kwargs={"k": 3}  # Number of documents to retrieve

# Adjust similarity threshold
search_kwargs={"score_threshold": 0.7}  # 70% minimum match
```

### Caching Strategy

```bash
# Enable caching
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600  # 1 hour

# Cache hit rates in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace DocumentMind \
  --metric-name CacheHitRate
```

### Worker Configuration

```bash
# Production: 4 workers (1 per CPU)
WORKERS=4

# For 8-core instance
WORKERS=8

# For lambda
# Lambda auto-scales, no configuration needed
```

---

## Security Hardening

### API Security

- ✅ Always require `x-api-key` header in production
- ✅ Rotate API keys every 90 days
- ✅ Use strong, cryptographically secure keys
- ✅ Store keys in AWS Secrets Manager, never in code

### Network Security

- ✅ Use VPC for ECS tasks
- ✅ Enable Security Groups restrictions
- ✅ Use NLB/ALB for load balancing
- ✅ Enable WAF on API Gateway

### Data Security

- ✅ Enable S3 encryption for backups
- ✅ Enable HTTPS/TLS for all endpoints
- ✅ Enable KMS for CloudWatch Logs
- ✅ Regular security audits

---

## Cost Optimization

### Monthly Cost Breakdown

| Service           | Usage              | Estimate          |
| ----------------- | ------------------ | ----------------- |
| **ECS Fargate**   | 2 x 1GB, 168 hours | $30               |
| **ALB**           | 1 ALB, 1M requests | $25               |
| **Data Transfer** | 10 GB out          | $1                |
| **CloudWatch**    | Logs, metrics      | $5                |
| **S3 Backups**    | 20 GB stored       | $0.50             |
| **OpenAI API**    | ~10k queries       | Variable          |
| **Total**         |                    | **$61-100/month** |

### Cost Saving Tips

1. Use Fargate Spot (70% cheaper, 30% preemption risk)
2. Implement caching to reduce API calls
3. Use on-demand for critical tasks
4. Monitor CloudWatch Insights costs
5. Use S3 Intelligent Tiering for archives

---

## Troubleshooting

### Check Health

```bash
# API health
curl https://api.example.com/health

# Task health
aws ecs describe-tasks \
  --cluster documind-cluster \
  --tasks task-arn | jq '.tasks[0].healthStatus'

# Database connectivity
curl -X POST https://api.example.com/query?q=test \
  -H "x-api-key: key"
```

### Common Problems & Solutions

| Problem         | Diagnosis                | Solution                                |
| --------------- | ------------------------ | --------------------------------------- |
| High latency    | Check CloudWatch metrics | Increase worker count, check OpenAI API |
| 500 errors      | Check app logs           | Verify secrets, check rate limiting     |
| No backups      | Check S3 bucket          | Verify IAM permissions, cron job        |
| Memory pressure | Check task memory        | Increase ECS task memory limit          |

---

## Maintenance Tasks

### Daily

- [ ] Check CloudWatch dashboards
- [ ] Monitor error rates
- [ ] Review security logs

### Weekly

- [ ] Review cost metrics
- [ ] Check backup integrity
- [ ] Test critical endpoints

### Monthly

- [ ] Update dependencies
- [ ] Security audit
- [ ] Capacity review

### Quarterly

- [ ] Major version updates
- [ ] Disaster recovery drill
- [ ] Architecture review

---

## Documentation Links

- [AWS Deployment Guide](AWS_DEPLOYMENT.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [API Code Walkthrough](README.md#code-walkthrough)
- [Configuration Reference](./app/config.py)

---

**Last Updated:** January 2024
**Maintained By:** DevOps Team
