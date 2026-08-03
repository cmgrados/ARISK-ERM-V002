# 🔍 Monitoring & Observability Guide

## Overview

ARISK ERM includes comprehensive monitoring with:
- **Sentry**: Error tracking and performance monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

---

## Sentry Setup (Error Tracking)

### 1. Create Sentry Account
```
https://sentry.io/signup/
```

### 2. Configure Django Project
```
SENTRY_DSN=https://your-key@sentry.io/project-id
```

### 3. Test Error Tracking
```python
from sentry_sdk import capture_exception

try:
    # Your code
    pass
except Exception as e:
    capture_exception(e)  # Sends to Sentry
```

### 4. Access Dashboard
```
https://sentry.io/organizations/your-org/issues/
```

---

## Prometheus + Grafana Setup

### Start Monitoring Stack

```bash
# Option 1: Add monitoring services
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Option 2: Or start separately
docker run -d -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
```

### Access Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Configure Grafana

1. **Add Prometheus Data Source**
   - Data Sources → Prometheus
   - URL: http://prometheus:9090

2. **Import Dashboards**
   - Create new dashboard
   - Import JSON from monitoring/grafana/dashboards/

3. **Setup Alerts**
   - Alert Rules → New Rule
   - Set thresholds for critical metrics

---

## Key Metrics

### Application Metrics
```
arisk_requests_total          # Total HTTP requests
arisk_request_duration_seconds # Request latency
arisk_exceptions_total         # Total exceptions
arisk_api_errors_total         # API errors
```

### System Metrics
```
process_cpu_seconds_total
process_resident_memory_bytes
python_gc_collections_total
```

### Database Metrics
```
pg_stat_activity_connections
pg_stat_database_tup_returned
pg_stat_database_tup_fetched
```

### Cache Metrics
```
redis_connected_clients
redis_used_memory
redis_commands_processed_total
```

---

## Alert Examples

### High Error Rate
```yaml
- alert: HighErrorRate
  expr: rate(arisk_exceptions_total[5m]) > 10
  for: 5m
  annotations:
    summary: "High error rate detected"
```

### Slow Requests
```yaml
- alert: SlowRequests
  expr: histogram_quantile(0.95, arisk_request_duration_seconds) > 1
  for: 5m
  annotations:
    summary: "P95 request duration exceeds 1s"
```

### High Memory Usage
```yaml
- alert: HighMemory
  expr: process_resident_memory_bytes / (1024*1024) > 500
  for: 5m
  annotations:
    summary: "Process using > 500MB memory"
```

---

## Performance Optimization

### Django
```python
# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Query optimization
from django.db.models import prefetch_related_objects
prefetch_related_objects(users, 'profile')
```

### Database
```sql
-- Monitor slow queries
SELECT query, mean_exec_time FROM pg_stat_statements
ORDER BY mean_exec_time DESC;

-- Create indexes
CREATE INDEX idx_customer_dni ON customer(dni);
CREATE INDEX idx_operation_customer ON credit_operation(customer_id);
```

### Redis
```bash
# Monitor Redis
docker-compose exec redis redis-cli
INFO server
SLOWLOG GET 10
```

---

## Logging

### View Logs
```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# All services
docker-compose logs -f
```

### Log Levels
```
DEBUG   - Development information
INFO    - General informational messages
WARNING - Warning messages for problematic situations
ERROR   - Error messages
CRITICAL - Critical errors requiring immediate attention
```

---

## Checklist

- [ ] Sentry account created and configured
- [ ] SENTRY_DSN in .env
- [ ] Prometheus running and scraping metrics
- [ ] Grafana dashboards created
- [ ] Alert rules configured
- [ ] Log aggregation enabled
- [ ] Performance baselines established
- [ ] On-call escalation configured

---

**Monitoring is critical for production reliability.**

See DOCKER_QUICKSTART.md for deployment instructions.
