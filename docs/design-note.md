# Asset Tracker API — Scaling Design Note

## Goal and assumptions
The target is 10,000 requests per minute, or about 167 requests per second on average. Traffic may peak above this rate. The current service uses FastAPI and SQLite, and the proposed changes would be measured before production rollout.

## Likely bottlenecks
SQLite may become a bottleneck when many requests write at the same time because writes are serialized. Database queries, connection handling, and expensive synchronous operations could also increase response times. The actual bottleneck must be confirmed through profiling and load tests.

## Database and indexes
For sustained concurrent traffic, I would migrate SQLite to PostgreSQL. I would review query plans and add indexes to frequently filtered or joined columns, such as asset IDs, employee IDs, and active assignments. Existing uniqueness and foreign-key rules must remain enforced. Connection pooling would limit the number of open database connections.

## Concurrency and reliability
I would keep transactions short and use database constraints to prevent duplicate active assignments. I would set connection and request timeouts, handle transient database errors safely, and ensure rejected operations do not leave partial changes. Any retries would be limited to safe operations.

## Scaling the service
I would run multiple FastAPI instances behind a load balancer and keep application instances stateless. Shared state would live in PostgreSQL rather than a local database file. If measurements showed a need, I would add caching for frequently read data and move slow background work to a task queue.

## Measuring success
I would run repeatable load tests at increasing request rates, including the target of 10,000 requests per minute and higher peak traffic. I would measure throughput, p50/p95/p99 latency, error rate, CPU and memory use, database connection usage, lock waits, and slow queries. I would compare results before and after each change and check that all API tests still pass.

## Conclusion
I would first establish a baseline, identify the actual bottleneck, and improve the database and connection strategy before adding more infrastructure. The target is a design goal, not a claim that the current implementation has already achieved this throughput.
