# Performance Optimization Guide

## Optimizations Implemented

### Database
- ✅ Connection pooling
- ✅ Async database operations
- ✅ Query optimization
- ✅ Indexed columns
- ✅ Efficient joins

### API
- ✅ Response caching
- ✅ Parallel query execution
- ✅ Pagination
- ✅ Lazy loading relationships

### Code
- ✅ Async/await for I/O operations
- ✅ Efficient data structures
- ✅ Minimal database queries

## Performance Metrics

### Target Response Times
- Health check: < 10ms
- Simple queries: < 50ms
- Complex queries: < 200ms
- Dashboard endpoints: < 500ms

### Database Optimization

#### Indexes
Ensure indexes on frequently queried columns:
```sql
-- Example indexes
CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_invoices_status ON invoices(status);
```

#### Query Optimization
- Use `select_related` for foreign keys
- Use `prefetch_related` for many-to-many
- Avoid N+1 queries
- Use aggregation queries

### Caching Strategy

#### Response Caching
```python
from app.core.cache import cached

@cached(ttl_seconds=300)
async def get_dashboard_data():
    # Expensive operation
    ...
```

#### Cache Invalidation
```python
# Invalidate cache on data updates
cache.delete(f"dashboard:{user_id}")
```

### API Optimization

#### Pagination
Always paginate large result sets:
```python
# Limit results
results = await db.execute(
    select(Model).limit(20).offset(page * 20)
)
```

#### Parallel Queries
Use `asyncio.gather` for independent queries:
```python
results = await asyncio.gather(
    get_patients(),
    get_appointments(),
    get_revenue(),
)
```

## Performance Monitoring

### Metrics to Track
- Request duration
- Database query time
- Cache hit rate
- Error rate
- Throughput (requests/second)

### Tools
- Application Performance Monitoring (APM)
- Database query profiling
- Load testing (Locust, k6)

## Production Optimizations

### 1. Use Redis for Caching
```python
import redis
redis_client = redis.Redis(host='localhost', port=6379)
```

### 2. Database Connection Pooling
```python
# Configure pool size
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
)
```

### 3. CDN for Static Assets
- Serve static files via CDN
- Enable compression
- Use browser caching

### 4. Database Replication
- Read replicas for read-heavy operations
- Master-slave setup

### 5. Load Balancing
- Multiple application instances
- Round-robin or least-connections

## Performance Testing

### Load Testing
```bash
# Using Locust
locust -f load_test.py --host=http://localhost:8000
```

### Benchmarking
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/v1/health
```

## Optimization Checklist

- [x] Database indexes on foreign keys
- [x] Connection pooling
- [x] Async operations
- [x] Response caching
- [x] Pagination
- [ ] Redis caching (production)
- [ ] Database query optimization
- [ ] CDN setup
- [ ] Load balancing
- [ ] Monitoring and alerting
