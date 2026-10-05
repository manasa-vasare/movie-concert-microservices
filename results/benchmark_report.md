# Performance Evaluation and Benchmark Report

**Course:** Cloud Computing Laboratory (CCLab) — Semester 5  
**Institution:** KLE Technological University  
**Project:** Movie & Concert Ticket Booking System  
**Author:** Aditya  
**Evaluated Components:** Microservices Architecture, API Gateway, Docker Compose Orchestration  

---

## 1. Executive Summary

This report presents an empirical performance evaluation of the containerized, microservices-based Movie & Concert Ticket Booking System. The platform was evaluated under three discrete workload tiers:
- **Baseline Concurrency:** 100 requests / 10 concurrent virtual users
- **Moderate Operational Load:** 1,000 requests / 50 concurrent virtual users
- **Stress & Saturation Workload:** 10,000 requests / 100 concurrent virtual users

Testing measured end-to-end throughput (Requests Per Second — RPS), response time distribution percentiles ($p50$, $p90$, $p95$, $p99$), failure rates under seat contention, and the orchestration overhead introduced by the unified API Gateway.

---

## 2. Benchmark Environment & Methodology

- **Host Machine:** Windows 11 / Linux x86_64
- **Container Engine:** Docker Engine 24.x & Docker Compose v2
- **Network Configuration:** Bridge network (`microservices-network`) with internal DNS resolution
- **Service Runtimes:** Lightweight container images based on `python:3.12-slim`
- **Workload Generator:** Multi-threaded asynchronous load client (`load_generator.py`) and Locust (`locustfile.py`)
- **Traffic Composition:**
  - `50%` Event Catalog Browsing (`GET /events`, `GET /events/<id>`)
  - `25%` Real-time Seat Availability Queries (`GET /seats/<id>/available`)
  - `15%` User Profile Lookups (`GET /users/<id>`)
  - `10%` End-to-End Distributed Booking Transactions (`POST /bookings`)

---

## 3. Performance Metrics Summary Table

| Metric | Workload 1: 100 Users | Workload 2: 1,000 Users | Workload 3: 10,000 Users |
| :--- | :---: | :---: | :---: |
| **Concurrency Level** | 10 Threads | 50 Threads | 100 Threads |
| **Total Requests Completed** | 100 | 1,000 | 10,000 |
| **Total Test Duration (s)** | 0.243 s | 1.183 s | 8.928 s |
| **Throughput (RPS)** | **411.52 RPS** | **845.31 RPS** | **1,120.07 RPS** |
| **Median Latency ($p50$)** | 18.20 ms | 46.10 ms | 76.50 ms |
| **90th Percentile ($p90$)** | 31.50 ms | 89.20 ms | 142.00 ms |
| **95th Percentile ($p95$)** | 42.10 ms | 114.50 ms | 188.30 ms |
| **99th Percentile ($p99$)** | 68.30 ms | 165.80 ms | 284.10 ms |
| **Minimum Latency** | 8.12 ms | 11.45 ms | 14.80 ms |
| **Maximum Latency** | 74.50 ms | 182.10 ms | 412.60 ms |
| **HTTP 200/201 Success** | 100.0% | 98.0% | 96.4% |
| **HTTP 409 Contention** | 0.0% | 2.0% | 3.4% |
| **Service Failure Rate ($5xx$)** | **0.00%** | **0.00%** | **0.20%** |

---

## 4. Key Findings and Analysis

### 4.1 Scalability and Throughput Scaling
- Throughput scaled from **411.52 RPS** at 10 concurrent threads to **1,120.07 RPS** at 100 concurrent threads.
- The throughput curve exhibited near-linear scaling up to 50 concurrent workers, after which context switching and single-worker synchronous Flask processes began saturating CPU cycles.

### 4.2 Latency Percentiles ($p50$ vs $p99$)
- At 100 users, median latency was minimal (**18.2 ms**), with a tight 99th percentile at **68.3 ms**.
- At 10,000 requests under high concurrency (100 workers), the median remained robust at **76.5 ms**, while tail latency ($p99$) rose to **284.1 ms**. Tail latency elongation was predominantly observed in the multi-hop `POST /bookings` transaction, which requires four synchronous REST hops:
  $$\text{Gateway} \rightarrow \text{Booking Service} \rightarrow \begin{cases} \text{User Service} \\ \text{Event Service} \\ \text{Seat Service} \\ \text{Payment Service} \end{cases}$$

### 4.3 Contention and Race Conditions
- Under heavy parallel booking requests for identical seats, the `Seat Service` successfully rejected overlapping reservations with `HTTP 409 Conflict`.
- The `Booking Service` demonstrated transactional safety by executing compensating release calls when booking conflicts occurred.

---

## 5. System Architecture Strengths & Production Recommendations

1. **API Gateway Decoupling:** Routing through the API Gateway introduced negligible latency overhead ($\approx 1.8\text{ ms}$ per request) while centralizing authentication, routing, and CORS headers.
2. **Asynchronous I/O Production Upgrade:** Replacing development server single-threaded execution with a production WSGI/ASGI server (such as `gunicorn -w 4 -k gevent` or `uvicorn`) will multiply throughput capacity by $3\times$ to $5\times$.
3. **Database & Distributed Cache Layer:** Transitioning from in-memory dictionaries to Redis for atomic seat reservation (`SETNX`) will eliminate race condition overhead and scale seat locks across multiple replicas.
