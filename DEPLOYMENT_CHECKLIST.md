# Deployment Checklist

## Pre-Deployment Tasks

### Code & Configuration
- [ ] All code committed to git
- [ ] Environment variables documented in `.env` template
- [ ] API endpoints tested locally
- [ ] Frontend fully integrated with backend
- [ ] No hardcoded secrets in code
- [ ] API_BASE_URL correctly set for target environment
- [ ] CORS settings appropriate for deployment domain

### Testing
- [ ] Backend API health check passing
- [ ] All API endpoints returning expected responses
- [ ] Frontend loads without console errors
- [ ] Questionnaire completes successfully
- [ ] Results display correctly
- [ ] PDF generation works
- [ ] Firebase authentication functional (if using)
- [ ] Firestore database accessible (if storing data)
- [ ] Mobile responsive design verified

### Documentation
- [ ] README updated with deployment instructions
- [ ] API documentation complete
- [ ] Database schema documented
- [ ] Environment variables documented
- [ ] Security considerations noted
- [ ] Troubleshooting guide created

### Security
- [ ] API input validation enabled
- [ ] CORS properly configured
- [ ] Sensitive data not in logs
- [ ] HTTPS enabled in production
- [ ] Database security rules configured
- [ ] API rate limiting considered
- [ ] Error messages don't expose sensitive info
- [ ] Dependencies updated for security patches

## Local Docker Testing

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up

# 3. Test frontend
#    Open http://localhost in browser

# 4. Test API
#    curl http://localhost/api/questions

# 5. View logs
#    docker-compose logs -f backend
#    docker-compose logs -f frontend

# 6. Stop services
#    docker-compose down
```

- [ ] Docker images build without errors
- [ ] Services start successfully
- [ ] Frontend accessible on port 80
- [ ] Backend API accessible through frontend proxy
- [ ] Database connections working
- [ ] All endpoints functional
- [ ] No errors in service logs

## Deployment Environments

### Development (Local)
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Backend running on port 5000
- [ ] Frontend running on port 8000
- [ ] CORS enabled for localhost

### Staging (Pre-production)
- [ ] Docker images pushed to registry
- [ ] Environment variables configured
- [ ] SSL/TLS certificate obtained
- [ ] Database backup configured
- [ ] Error logging enabled
- [ ] Performance monitoring set up
- [ ] Health checks configured
- [ ] Auto-scaling (if cloud deployment)

### Production
- [ ] Cloud infrastructure provisioned
- [ ] Docker images deployed
- [ ] Environment variables securely stored
- [ ] SSL/TLS certificate installed
- [ ] WAF/DDoS protection enabled
- [ ] Database backups automated
- [ ] Monitoring and alerting active
- [ ] Log aggregation configured
- [ ] Disaster recovery plan documented
- [ ] Update strategy planned

## Cloud Deployment Options

### Google Cloud Run (Recommended)

```bash
# 1. Build image
docker build -t gcr.io/PROJECT_ID/autism-api app/api/

# 2. Push to registry
docker push gcr.io/PROJECT_ID/autism-api

# 3. Deploy
gcloud run deploy autism-api \
  --image gcr.io/PROJECT_ID/autism-api \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --set-env-vars GROQ_API_KEY=xxx

# 4. Frontend to Firebase Hosting
firebase deploy --only hosting
```

- [ ] Google Cloud project created
- [ ] Docker image pushed to GCR
- [ ] Cloud Run service deployed
- [ ] Environment variables set
- [ ] Firebase Hosting configured
- [ ] Custom domain configured
- [ ] SSL certificate active

### AWS (Alternative)

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin xxx.dkr.ecr.us-east-1.amazonaws.com
docker push xxx.dkr.ecr.us-east-1.amazonaws.com/autism-api

# Deploy to ECS or EKS
# Frontend to S3 + CloudFront
```

- [ ] ECR repository created
- [ ] Image pushed to ECR
- [ ] ECS/Lambda deployment configured
- [ ] S3 bucket for frontend created
- [ ] CloudFront distribution set up
- [ ] IAM roles configured
- [ ] RDS/DynamoDB configured

### Azure (Alternative)

```bash
# Push to ACR
az acr build --registry myregistry --image autism-api app/api/

# Deploy to App Service
az containerapp create --name autism-api ...

# Frontend to Static Web Apps
```

- [ ] Azure Container Registry created
- [ ] Image pushed to ACR
- [ ] Container App deployed
- [ ] App Service configured
- [ ] Cosmos DB configured
- [ ] Authentication configured

## Post-Deployment

### Verification
- [ ] Frontend accessible via public URL
- [ ] All pages load without errors
- [ ] API endpoints responding correctly
- [ ] Database connections stable
- [ ] Authentication working
- [ ] Results persisting in database
- [ ] PDF generation functional

### Monitoring
- [ ] Uptime monitoring enabled
- [ ] Error tracking active
- [ ] Performance metrics collected
- [ ] Log aggregation working
- [ ] Alerts configured for errors
- [ ] Health check endpoint monitored
- [ ] Database performance monitored

### Performance
- [ ] API response time < 2 seconds
- [ ] Frontend load time < 3 seconds
- [ ] PDF generation time < 10 seconds
- [ ] Database queries optimized
- [ ] Caching enabled where possible
- [ ] CDN configured for static files

### Security
- [ ] HTTPS enforced
- [ ] Security headers set
- [ ] API rate limiting active
- [ ] Database encrypted at rest
- [ ] Database encrypted in transit
- [ ] Regular security audits scheduled
- [ ] Dependency scanning enabled

### Backup & Disaster Recovery
- [ ] Daily database backups
- [ ] Backup tested for restoration
- [ ] Disaster recovery plan documented
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined
- [ ] Backup retention policy set

## Maintenance Schedule

### Daily
- [ ] Monitor error logs
- [ ] Check system health dashboard
- [ ] Verify backup completion

### Weekly
- [ ] Review performance metrics
- [ ] Check for security advisories
- [ ] Update dependency status

### Monthly
- [ ] Security patch review
- [ ] Database optimization review
- [ ] Cost analysis
- [ ] User feedback review

### Quarterly
- [ ] Full security audit
- [ ] Disaster recovery drill
- [ ] Performance analysis
- [ ] Capacity planning review

## Rollback Plan

If deployment fails:

```bash
# Docker Rollback
docker-compose down
docker-compose up  # with previous version

# Cloud Rollback (Google Cloud Run)
gcloud run deploy autism-api --image gcr.io/PROJECT_ID/autism-api:previous-tag

# Database Rollback
# Restore from latest backup
```

- [ ] Previous version tags maintained
- [ ] Rollback procedure documented
- [ ] Database backup available
- [ ] Zero-downtime deployment strategy

## Sign-Off

- [ ] Project Manager Approval: _______________
- [ ] Security Team Approval: _______________
- [ ] DevOps Team Approval: _______________
- [ ] QA Team Approval: _______________
- [ ] Deployment Date: _______________
- [ ] Deployed By: _______________

## Post-Deployment Review

After 1 week:
- [ ] No critical errors reported
- [ ] Performance metrics acceptable
- [ ] User feedback positive
- [ ] Database functioning normally
- [ ] Backups working correctly

After 1 month:
- [ ] System stable and reliable
- [ ] All features working as expected
- [ ] Performance optimizations completed
- [ ] Monitoring alerts tuned
- [ ] Cost within budget

---

**Use this checklist to ensure smooth deployment!**

For detailed deployment instructions, see:
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Detailed setup
- [README_INTEGRATED.md](README_INTEGRATED.md) - Feature overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
