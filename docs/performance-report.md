# Asset Tracker API - Load Test Report

## Test Environment

- Machine: ASUS TUF Gaming F16 FX607VJB
- Processor: Intel Core 5 210H
- RAM: 15.63 GB
- Tool: Locust 2.47.0
- Dataset: 1,001 assets
- Endpoint: GET /assets?limit=100&offset=0
- Test duration: 60 seconds per test
- Server: Local Uvicorn development server

## Test Commands

10 concurrent users:

python -m locust -f locustfile.py --headless -H http://127.0.0.1:8000 -u 10 -r 2 -t 60s --csv results_10_users --csv-full-history

50 concurrent users:

python -m locust -f locustfile.py --headless -H http://127.0.0.1:8000 -u 50 -r 5 -t 60s --csv results_50_users --csv-full-history

## Results

| Metric | 10 Users | 50 Users |
|---|---:|---:|
| Duration | 60 seconds | 60 seconds |
| Total requests | 573 | 2,746 |
| Failed requests | 0 | 0 |
| Failure rate | 0% | 0% |
| Throughput | 9.69 req/s | 46.32 req/s |
| Average response time | 5 ms | 6 ms |
| Approximate p95 latency | 9 ms | 13 ms |
| Maximum response time | 34 ms | 33 ms |

## Observations

Both tests completed with zero reported failures. The 50-user test
achieved higher throughput, with a modest increase in p95 latency.

## Limitations

These are local development measurements, not production benchmarks.
Only the first page of the asset listing endpoint was tested. Results
may vary with machine load and configuration.

## Reproduction

1. Install project dependencies and Locust.
2. Seed the synthetic dataset.
3. Start the API using:
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
4. Run the two Locust commands listed above.
5. Compare the new results with this report.

The recorded figures above are from the completed test runs.
