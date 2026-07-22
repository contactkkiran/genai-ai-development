# Production Deployment Checklist

## Pre-Deployment

- [ ] **Environment Variables**
  - [ ] Set `ENVIRONMENT=production`
  - [ ] Set `DEBUG=false`
  - [ ] Configure `OPENAI_API_KEY` in AWS Secrets Manager
  - [ ] Generate strong `API_KEY_SECRET`
  - [ ] Configure `ALLOWED_ORIGINS` for CORS

- [ ] **Security**
  - [ ] Review CORS allowed origins (no wildcards!)
  - [ ] Enable API authentication headers
  - [ ] Configure rate limiting thresholds
  - [ ] Set up SSL/TLS certificates
  - [ ] Enable WAF on API Gateway/ALB

- [ ] **Database**
  - [ ] Create S3 backup bucket
  - [ ] Test backup restore procedure
  - [ ] Configure automated backups
  - [ ] Verify database encryption

- [ ] **Logging & Monitoring**
  - [ ] Set up CloudWatch Log Groups
  - [ ] Configure log retention (30 days)
  - [ ] Enable X-Ray tracing
  - [ ] Set up Sentry error tracking
  - [ ] Create CloudWatch alarms

- [ ] **Performance**
  - [ ] Set `RATE_LIMIT_PER_MINUTE` appropriately
  - [ ] Configure caching TTL
  - [ ] Test with production data volume
  - [ ] Load test the endpoints

- [ ] **Documentation**
  - [ ] Update README with production setup
  - [ ] Document API endpoints
  - [ ] Create runbooks for common issues
  - [ ] Document backup/recovery procedures

## Testing

- [ ] **Unit Tests**

  ```bash
  pytest app/ -v
  ```

- [ ] **Integration Tests**
  - [ ] Test `/health` endpoint
  - [ ] Test `/ingest` with API key
  - [ ] Test `/query` with various queries
  - [ ] Test rate limiting
  - [ ] Test error handling

- [ ] **Load Testing**

  ```bash
  locust -f locustfile.py --host=http://localhost:8000
  ```

- [ ] **Security Testing**
  - [ ] Test without API key (should fail in prod)
  - [ ] Test SQL injection attempts
  - [ ] Test large payload handling
  - [ ] Test XSS protection

## Deployment

- [ ] **Docker**
  - [ ] Build image: `docker build -t documind-ai:latest .`
  - [ ] Test locally: `docker run -p 8000:8000 documind-ai:latest`
  - [ ] Push to ECR: `docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/documind-ai:latest`

- [ ] **AWS Services**
  - [ ] Verify ECS Task Definition
  - [ ] Create/update ECS Service
  - [ ] Configure ALB/NLB
  - [ ] Set up auto-scaling
  - [ ] Configure health checks

- [ ] **Secrets Management**
  - [ ] Store secrets in AWS Secrets Manager
  - [ ] Test secret retrieval in task definition
  - [ ] Verify IAM role permissions

- [ ] **Networking**
  - [ ] Configure Security Groups
  - [ ] Set up VPC endpoints (if needed)
  - [ ] Configure DNS/Route53
  - [ ] Enable CloudFront (optional)

## Post-Deployment

- [ ] **Verification**
  - [ ] Health check: `curl https://api.example.com/health`
  - [ ] Test query endpoint with valid API key
  - [ ] Monitor CloudWatch metrics
  - [ ] Check error logs in CloudWatch

- [ ] **Monitoring Setup**
  - [ ] Create CloudWatch dashboard
  - [ ] Set up SNS notifications
  - [ ] Configure PagerDuty/Slack alerts
  - [ ] Test alert routing

- [ ] **Documentation Updates**
  - [ ] Document production endpoints
  - [ ] Add troubleshooting section
  - [ ] Update API documentation
  - [ ] Create incident response playbook

- [ ] **Backup Verification**
  - [ ] Verify S3 backups are running
  - [ ] Test restore from backup
  - [ ] Document recovery time objective (RTO)
  - [ ] Document recovery point objective (RPO)

## Ongoing Maintenance

- [ ] **Daily**
  - [ ] Check CloudWatch alarms
  - [ ] Monitor error rates
  - [ ] Review logs for issues

- [ ] **Weekly**
  - [ ] Review metrics and trends
  - [ ] Check backup integrity
  - [ ] Review security logs

- [ ] **Monthly**
  - [ ] Review cost analysis
  - [ ] Update dependencies
  - [ ] Security audit
  - [ ] Disaster recovery drill

- [ ] **Quarterly**
  - [ ] Major version updates
  - [ ] Architecture review
  - [ ] Capacity planning
  - [ ] Security assessment

## Rollback Procedure

If deployment issues occur:

```bash
# Revert to previous task definition
aws ecs update-service \
  --cluster documind-cluster \
  --service documind-service \
  --task-definition documind-ai:PREVIOUS_VERSION

# Restore database from S3 backup
aws s3 sync s3://documind-ai-db/backups/BACKUP_DATE/ /data/db/

# Restart service
aws ecs update-service \
  --cluster documind-cluster \
  --service documind-service \
  --force-new-deployment
```

## Success Criteria

- ✅ `/health` endpoint returns 200 OK
- ✅ Queries respond within 2 seconds
- ✅ Error rate < 0.1%
- ✅ API key authentication working
- ✅ Rate limiting enforced
- ✅ Logs being written to CloudWatch
- ✅ Backups created successfully
- ✅ Monitoring alerts configured
- ✅ No security warnings in logs

---

**Deployment Date:** ******\_\_\_\_******
**Deployed By:** ******\_\_\_\_******
**Approved By:** ******\_\_\_\_******
**Notes:**
