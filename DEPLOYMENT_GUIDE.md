# AUTOOS - Omega Edition: Deployment Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM minimum (16GB recommended)
- API keys for LLM providers

### Step 1: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd autoos-omega

# Copy environment template
cp .env.example .env
```

### Step 2: Add API Keys

Edit `.env` and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional
GOOGLE_API_KEY=your-google-key-here
```

### Step 3: Start All Services

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Step 4: Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:45Z",
#   "version": "1.0.0",
#   "components": {
#     "api": "healthy",
#     "session_memory": "healthy",
#     "working_memory": "healthy",
#     "event_bus": "healthy"
#   }
# }
```

## 📊 Access Monitoring

- **API**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **API Docs**: http://localhost:8000/docs

## 🎯 Submit Your First Intent

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-123" \
  -d '{
    "intent": "Analyze system logs and identify errors",
    "user_id": "user-dev",
    "context": {
      "priority": "high"
    }
  }'

# Response:
# {
#   "workflow_id": "wf-abc123",
#   "status": "pending",
#   "estimated_cost": 0.15,
#   "estimated_time": 45.0,
#   "message": "Intent submitted successfully"
# }
```

## 🔍 Check Workflow Status

```bash
curl http://localhost:8000/api/v1/workflows/wf-abc123 \
  -H "X-API-Key: dev-key-123"
```

## 📈 View Metrics

```bash
curl http://localhost:8000/metrics
```

## 🛠️ Development Mode

### Run Services Locally

```bash
# Start infrastructure only
docker-compose up redis postgres chromadb -d

# Install dependencies
pip install -r requirements.txt

# Run API locally
uvicorn autoos.intent.api:app --reload --host 0.0.0.0 --port 8000

# Run orchestrator (in another terminal)
python -m autoos.orchestration.orchestrator_service

# Run agent worker (in another terminal)
python -m autoos.execution.agent_worker_service
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/autoos --cov-report=html

# Property-based tests only
pytest tests/property/

# Integration tests
pytest tests/integration/
```

## 🔧 Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Agent Configuration
MAX_CONCURRENT_AGENTS=10
AGENT_TIMEOUT_SECONDS=300
DEFAULT_CONFIDENCE_THRESHOLD=0.75

# Workflow Configuration
WORKFLOW_MAX_RETRIES=3
WORKFLOW_RETRY_BACKOFF_MULTIPLIER=2.0

# Cost Tracking
COST_ALERT_THRESHOLD_USD=100.0
COST_TRACKING_ENABLED=true

# Security
SECRET_ENCRYPTION_KEY=generate-with-fernet-key
JWT_SECRET_KEY=change-this-jwt-secret

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 📊 Monitoring Setup

### Grafana Dashboards

1. Access Grafana: http://localhost:3000
2. Login: admin/admin
3. Add Prometheus data source:
   - URL: http://prometheus:9090
   - Save & Test

4. Import dashboards from `config/grafana/dashboards/`

### Key Metrics to Monitor

- `autoos_workflow_total` - Workflow count by status
- `autoos_workflow_duration_seconds` - Execution time
- `autoos_workflow_cost_dollars` - Cost per workflow
- `autoos_llm_latency_seconds` - LLM response time
- `autoos_agent_active` - Active agent count
- `autoos_failures_total` - Failure count by type
- `autoos_recovery_success_rate` - Recovery success percentage

## 🔐 Security

### API Authentication

Default API keys (change in production):

```bash
# Development
X-API-Key: dev-key-123

# Production
X-API-Key: prod-key-456
```

### Generate Secure API Keys

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Trust Levels

- **RESTRICTED**: Read-only operations
- **STANDARD**: Read/write, HTTP requests
- **ELEVATED**: Command execution
- **PRIVILEGED**: All operations

## 📦 Production Deployment

### Scaling

Scale agent workers:

```bash
docker-compose up -d --scale agent-worker=10
```

### High Availability

1. **API Layer**: Run multiple instances behind load balancer
2. **Redis**: Use Redis Sentinel for HA
3. **PostgreSQL**: Set up replication
4. **Vector DB**: Regular backups

### Resource Requirements

**Minimum (Development)**:
- 2 CPU cores
- 8GB RAM
- 20GB disk

**Recommended (Production)**:
- 8 CPU cores
- 32GB RAM
- 100GB SSD

**Per Agent Worker**:
- 0.5 CPU cores
- 2GB RAM

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart api

# Rebuild containers
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U autoos -d autoos -c "SELECT 1;"

# Check Redis
docker-compose exec redis redis-cli ping
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce concurrent agents in .env
MAX_CONCURRENT_AGENTS=5
```

### LLM Provider Failures

Check logs for fallback behavior:

```bash
docker-compose logs | grep "llm.fallback_triggered"
```

System automatically tries alternative providers.

### Workflow Stuck

```bash
# Check workflow state
curl http://localhost:8000/api/v1/workflows/wf-abc123 \
  -H "X-API-Key: dev-key-123"

# Resume workflow
curl -X POST http://localhost:8000/api/v1/workflows/wf-abc123/resume \
  -H "X-API-Key: dev-key-123"
```

## 🔄 Backup & Recovery

### Backup PostgreSQL

```bash
docker-compose exec postgres pg_dump -U autoos autoos > backup.sql
```

### Restore PostgreSQL

```bash
docker-compose exec -T postgres psql -U autoos autoos < backup.sql
```

### Backup Vector DB

```bash
docker-compose exec chromadb tar -czf /tmp/chroma-backup.tar.gz /chroma/chroma
docker cp autoos-chromadb:/tmp/chroma-backup.tar.gz ./chroma-backup.tar.gz
```

## 📝 Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api

# Search logs
docker-compose logs | grep "workflow_id=wf-abc123"
```

### Log Levels

Set in `.env`:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🚦 Health Checks

All services include health checks:

```bash
# API
curl http://localhost:8000/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

## 🔧 Maintenance

### Update System

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose up -d --build

# Check status
docker-compose ps
```

### Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove unused images
docker system prune -a
```

## 📞 Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Logs**: Check `docker-compose logs`
- **Metrics**: http://localhost:9090

## ✅ Production Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate secure API keys
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up log aggregation
- [ ] Configure alerting
- [ ] Test backup/restore procedures
- [ ] Set up monitoring dashboards
- [ ] Document runbooks
- [ ] Test failure scenarios
- [ ] Configure rate limiting
- [ ] Set up Redis Sentinel
- [ ] Configure PostgreSQL replication
- [ ] Test horizontal scaling
- [ ] Review security policies
- [ ] Set up cost alerts

---

**AUTOOS is now running. The system is self-healing, observable, and ready for production workloads.**
