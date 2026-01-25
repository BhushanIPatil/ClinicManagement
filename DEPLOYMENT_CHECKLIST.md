# Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All tests passing (`pytest` and `npm test`)
- [ ] Code coverage > 80%
- [ ] No linter errors
- [ ] Code review completed
- [ ] Security audit passed

### Environment Configuration
- [ ] Environment variables configured
- [ ] Database credentials set
- [ ] API keys configured
- [ ] CORS origins configured
- [ ] Debug mode disabled

### Database
- [ ] Database migrations up to date
- [ ] Database backups configured
- [ ] Indexes created
- [ ] Connection pooling configured
- [ ] Database user permissions set

### Security
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Authentication tested
- [ ] Authorization tested
- [ ] Secrets not in code

## Deployment Steps

### Backend Deployment

1. **Build Application**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Seed Initial Data**
   ```bash
   python scripts/seed_roles.py
   ```

4. **Start Application**
   ```bash
   # Development
   uvicorn app.main:app --reload
   
   # Production
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend Deployment

1. **Build Application**
   ```bash
   cd webapp
   npm install
   npm run build
   ```

2. **Deploy Build**
   ```bash
   # Copy dist/ to web server
   # Configure nginx/apache
   ```

### Infrastructure

- [ ] Server provisioned
- [ ] Domain configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup system configured

## Post-Deployment

### Verification
- [ ] Health check endpoint working
- [ ] API endpoints accessible
- [ ] Frontend loads correctly
- [ ] Authentication working
- [ ] Database connections working
- [ ] Error handling working

### Monitoring
- [ ] Application logs monitored
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring active
- [ ] Uptime monitoring configured
- [ ] Alerting configured

### Documentation
- [ ] API documentation updated
- [ ] Deployment guide updated
- [ ] Runbook created
- [ ] Incident response plan

## Rollback Plan

1. **Database Rollback**
   ```bash
   alembic downgrade -1
   ```

2. **Application Rollback**
   - Revert to previous version
   - Restart application

3. **Frontend Rollback**
   - Deploy previous build
   - Clear CDN cache

## Environment-Specific Checklist

### Development
- [x] Local database running
- [x] Environment variables set
- [x] Debug mode enabled
- [x] Hot reload enabled

### Staging
- [ ] Staging database configured
- [ ] Staging environment variables
- [ ] Test data seeded
- [ ] Integration tests passing

### Production
- [ ] Production database configured
- [ ] Production environment variables
- [ ] Debug mode disabled
- [ ] Logging configured
- [ ] Monitoring active
- [ ] Backup system active
- [ ] Disaster recovery plan

## Deployment Tools

### Recommended
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Containers**: Docker, Kubernetes
- **Orchestration**: Docker Compose, Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack, Loki

### Example CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    - Run tests
    - Check coverage
  build:
    - Build Docker image
    - Push to registry
  deploy:
    - Deploy to production
```

## Common Issues

### Database Connection
- Check connection string
- Verify firewall rules
- Check database user permissions

### CORS Errors
- Verify CORS origins in settings
- Check frontend URL

### Authentication Issues
- Verify JWT secret
- Check token expiration
- Verify refresh token

### Performance Issues
- Check database indexes
- Verify connection pooling
- Check cache configuration
