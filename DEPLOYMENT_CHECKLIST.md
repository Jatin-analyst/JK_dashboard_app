# 🚀 Deployment Checklist

## Pre-Deployment Checks

### ✅ Code Quality
- [ ] All Python files pass syntax check (`python -m py_compile *.py`)
- [ ] No critical errors in application logs
- [ ] All imports resolve correctly
- [ ] Dashboard loads without errors locally

### ✅ Dependencies
- [ ] `requirements.txt` includes all necessary packages
- [ ] `requirements-prod.txt` contains minimal production dependencies
- [ ] No development-only packages in production requirements
- [ ] All package versions are pinned for reproducibility

### ✅ Data Files
- [ ] `data/city_day.csv` exists and is readable
- [ ] `data/station_day.csv` exists and is readable  
- [ ] `data/stations.csv` exists and is readable
- [ ] Data files contain expected columns and data types
- [ ] No sensitive information in data files

### ✅ Configuration
- [ ] `.streamlit/config.toml` configured for production
- [ ] Environment variables documented
- [ ] Security settings enabled (XSRF protection, CORS disabled)
- [ ] Appropriate port and address configuration

### ✅ Security
- [ ] No hardcoded secrets or API keys in code
- [ ] `.gitignore` excludes sensitive files
- [ ] `.streamlit/secrets.toml` not committed to version control
- [ ] Docker container runs as non-root user

## Deployment Options

### 🏠 Local Development
```bash
# Quick start
./deploy.bat local 8501
# or
python -m streamlit run app.py
```

### 🏭 Production Server
```bash
# Production deployment
./deploy.bat production 80
# or
streamlit run app.py --server.port=80 --server.address=0.0.0.0 --server.headless=true
```

### 🐳 Docker Deployment
```bash
# Docker Compose (recommended)
docker-compose up -d

# Direct Docker
docker build -t air-quality-dashboard .
docker run -p 8501:8501 air-quality-dashboard
```

### ☁️ Cloud Platforms

#### Streamlit Cloud
1. [ ] Repository is public or Streamlit Cloud has access
2. [ ] `requirements.txt` is in root directory
3. [ ] `app.py` is the main application file
4. [ ] Data files are included in repository or accessible via URL
5. [ ] No secrets in code (use Streamlit Cloud secrets management)

#### Heroku
1. [ ] `Dockerfile` is configured correctly
2. [ ] Port is configured via `$PORT` environment variable
3. [ ] Procfile created if needed: `web: streamlit run app.py --server.port=$PORT`

#### Railway/Render
1. [ ] Repository connected to platform
2. [ ] Build and start commands configured
3. [ ] Environment variables set if needed

#### AWS/GCP/Azure
1. [ ] Container registry access configured
2. [ ] Load balancer and health checks configured
3. [ ] Auto-scaling policies defined
4. [ ] Monitoring and logging enabled

## Post-Deployment Verification

### ✅ Functionality Tests
- [ ] Dashboard loads successfully
- [ ] All charts render correctly
- [ ] Filters work as expected
- [ ] Data quality reports display
- [ ] No JavaScript errors in browser console

### ✅ Performance Tests
- [ ] Page load time < 10 seconds
- [ ] Filter operations complete < 5 seconds
- [ ] Memory usage stable over time
- [ ] No memory leaks during extended use

### ✅ Health Monitoring
```bash
# Single health check
python monitor.py check

# Continuous monitoring
python monitor.py monitor --interval=60

# Performance metrics
python monitor.py metrics
```

### ✅ Load Testing (Optional)
```bash
# Install load testing tools
pip install locust

# Run basic load test
# (Create locustfile.py for specific tests)
```

## Troubleshooting

### Common Issues

#### Dashboard Won't Start
- Check Python version (3.8+ required)
- Verify all dependencies installed
- Check data files exist and are readable
- Review error logs for specific issues

#### Charts Not Displaying
- Verify plotly is installed correctly
- Check browser JavaScript console for errors
- Ensure data contains required columns
- Test with smaller dataset

#### Performance Issues
- Enable Streamlit caching
- Optimize data loading and processing
- Consider data sampling for large datasets
- Monitor memory usage

#### Docker Issues
- Verify Docker and Docker Compose installed
- Check port conflicts (8501)
- Review Docker logs: `docker-compose logs`
- Ensure sufficient disk space

### Monitoring Commands

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Monitor Docker containers
docker-compose ps
docker-compose logs -f

# Check resource usage
docker stats

# View application logs
tail -f /var/log/streamlit.log  # if logging to file
```

## Rollback Plan

### Quick Rollback Steps
1. [ ] Stop current deployment
2. [ ] Revert to previous working version
3. [ ] Restart with known good configuration
4. [ ] Verify functionality restored
5. [ ] Investigate and fix issues in development

### Docker Rollback
```bash
# Stop current containers
docker-compose down

# Revert to previous image
docker tag air-quality-dashboard:previous air-quality-dashboard:latest

# Restart
docker-compose up -d
```

## Success Criteria

### ✅ Deployment Successful When:
- [ ] Dashboard accessible at configured URL
- [ ] All features working as expected
- [ ] Performance meets requirements
- [ ] Health checks passing
- [ ] No critical errors in logs
- [ ] Monitoring systems operational

### 📊 Key Metrics to Monitor:
- **Uptime**: > 99.5%
- **Response Time**: < 5 seconds average
- **Error Rate**: < 1%
- **Memory Usage**: Stable, no leaks
- **CPU Usage**: < 80% average

## Maintenance

### Regular Tasks
- [ ] Monitor application logs weekly
- [ ] Update dependencies monthly
- [ ] Review performance metrics
- [ ] Backup data files regularly
- [ ] Test disaster recovery procedures

### Security Updates
- [ ] Monitor for security advisories
- [ ] Update base Docker images
- [ ] Review and rotate secrets
- [ ] Audit access permissions

---

**🎉 Deployment Complete!**

Your Air Quality Dashboard is now ready for production use. Remember to monitor the application regularly and keep dependencies updated for security and performance.