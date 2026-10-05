# Laboratory Verification Screenshots & Media Evidence

**Project:** Movie & Concert Ticket Booking System (Microservices Platform)  
**Course:** Cloud Computing Laboratory (CCLab) — Semester 5  
**Institution:** KLE Technological University  
**Student:** Aditya Rajashekhar Gavimath  
**Evaluation Manual:** `Microservice_Lab_Evaluation_Manual (1).pdf`  

This directory contains empirical evidence verifying the multi-container build, deployment, inter-service REST coordination, concurrency fault handling, telemetry, and automated load benchmarks.

---

## Screenshot 1: Multi-Container Parallel Image Compilation

![Screenshot 1](Screenshot%202026-10-05%20113856.png)

* **Executed Command:**
  ```powershell
  docker compose up --build -d
  ```
* **Evaluation Checkpoint:** **Checkpoint 2 — Multi-Container Docker Build**
* **Technical Description:**  
  Demonstrates Docker Compose coordinating parallel BuildKit image compilation for all 6 microservices (`api-gateway`, `booking-service`, `event-service`, `payment-service`, `seat-service`, `user-service`). Shows successful resolution of base image `python:3.12-slim`, layer caching for Python requirements (`pip install -r requirements.txt`), and context isolation for independent services.

---

## Screenshot 2: Container Lifecycle & Orchestrated Service Topology

![Screenshot 2](Screenshot%202026-10-05%20113936.png)

* **Executed Command:**
  ```powershell
  docker compose ps
  ```
* **Evaluation Checkpoint:** **Checkpoint 2 — Orchestration & Container Lifecycle Management**
* **Technical Description:**  
  Verifies that all 13 Docker Compose steps succeeded (`[+] up 13/13`), the bridge network `microservices-network` was established, and all 6 containers are actively running in status `Up`:
  * `api-gateway-container` on port `0.0.0.0:8000->8000/tcp`
  * `event-service-container` on port `0.0.0.0:5001->5000/tcp`
  * `user-service-container` on port `0.0.0.0:5002->5000/tcp`
  * `seat-service-container` on port `0.0.0.0:5003->5000/tcp`
  * `booking-service-container` on port `0.0.0.0:5004->5000/tcp`
  * `payment-service-container` on port `0.0.0.0:5005->5000/tcp`

---

## Screenshot 3: Distributed Saga Booking Transaction

![Screenshot 3](Screenshot%202026-10-05%20114109.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:5004/bookings" -Method POST -Body '{"user_id":3,"event_id":1,"seats":["A1","A2"]}' -ContentType "application/json"
  ```
* **Evaluation Checkpoint:** **Checkpoint 3 — Inter-Service REST Coordination & Distributed Saga**
* **Technical Description:**  
  Proves end-to-end multi-service business workflow. The Booking Service coordinates four distributed operations: validating User 3 via User Service, verifying Event 1 via Event Service, reserving seats `["A1", "A2"]` via Seat Service, and processing $1000 payment via Payment Service. The response confirms a successful booking with generated UUID receipt `receipt_f81b1567-27b0-4614-a957-3aa59868770c`.

---

## Screenshot 4: Concurrency Protection & Double-Booking Prevention

![Screenshot 4](Screenshot%202026-10-05%20114206.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:5004/bookings" -Method POST -Body '{"user_id":3,"event_id":1,"seats":["A1","A2"]}' -ContentType "application/json"
  ```
* **Evaluation Checkpoint:** **Checkpoint 3 — Fault Prevention, ACID Isolation & Error Handling**
* **Technical Description:**  
  Demonstrates concurrency safety. When a duplicate request attempts to reserve the already-booked seats `["A1", "A2"]`, the Seat Service denies the lock, and the Booking Service aborts with `HTTP 409 Conflict` (`"error": "Seat reservation failed"`), preventing double-booking and data corruption.

---

## Screenshot 5: Real-Time Multi-Container Resource Telemetry

![Screenshot 5](Screenshot%202026-10-05%20114243.png)

* **Executed Command:**
  ```powershell
  docker stats
  ```
* **Evaluation Checkpoint:** **Checkpoint 4 & 5 — Container Resource Monitoring**
* **Technical Description:**  
  Live telemetry capture across all 6 running containers. Proves that CPU consumption remains near zero (`0.00%`–`0.02%`) in steady-state, each Python Flask container consumes merely `20.6 MiB` to `24.1 MiB` of RAM (total RAM < 150 MiB), and thread/PID counts remain strictly isolated.

---

## Screenshot 6: API Gateway Aggregated Health Probe

![Screenshot 6](Screenshot%202026-10-05%20120240.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET | ConvertTo-Json -Depth 5
  ```
* **Evaluation Checkpoint:** **Checkpoint 1 & 2 — API Gateway Reverse Proxy & Centralized Probing**
* **Technical Description:**  
  Validates centralized health inspection through the API Gateway at port 8000. The Gateway asynchronously pings all 5 backend microservices and returns individual ping latencies: `booking_service` (5.66 ms), `event_service` (7.27 ms), `payment_service` (4.95 ms), `seat_service` (5.39 ms), `user_service` (6.11 ms), confirming total system health.

---

## Screenshot 7: API Gateway Reverse-Proxy Path Routing

![Screenshot 7](Screenshot%202026-10-05%20120721.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8000/movies" -Method GET | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Uri "http://localhost:8000/concerts" -Method GET | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Uri "http://localhost:8000/events" -Method GET | ConvertTo-Json -Depth 5
  ```
* **Evaluation Checkpoint:** **Checkpoint 2 — API Gateway Routing Contract**
* **Technical Description:**  
  Proves decoupled path routing. Requests to port 8000 are cleanly routed by the Gateway reverse proxy: `/movies` returns *Avengers: Secret Wars* at PVR Hubli, `/concerts` returns *Arijit Singh Live* at Bengaluru, and `/events` returns the aggregated catalog.

---

## Screenshot 8: Post-Redeployment Latency Verification

![Screenshot 8](Screenshot%202026-10-05%20120743.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET | ConvertTo-Json -Depth 5
  ```
* **Evaluation Checkpoint:** **Checkpoint 2 & 5 — Zero-Downtime Deployment & Steady-State Latency**
* **Technical Description:**  
  Validates that container recreation operates with zero system disruption. Inter-service latencies remain consistently sub-10ms across all microservices (`event_service`: 3.96 ms, `booking_service`: 6.69 ms, `payment_service`: 5.90 ms).

---

## Screenshot 9: Persistent Booking Retrieval & Audit Trail

![Screenshot 9](Screenshot%202026-10-05%20120815.png)

* **Executed Command:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:5004/bookings" -Method GET | ConvertTo-Json -Depth 5
  ```
* **Evaluation Checkpoint:** **Checkpoint 3 — Data Consistency & Audit History**
* **Technical Description:**  
  Verifies historical audit persistence in the Booking Service ledger. Successfully returns records for user `Aditya` (`id: 3`), confirmed seats `["A1", "A2"]`, event details, transaction ID, and booking status `confirmed`.

---

## Screenshot 10: Automated High-Concurrency Load Testing

![Screenshot 10](Screenshot%202026-10-05%20120852.png)

* **Executed Command:**
  ```powershell
  python load_generator.py -n 200 -c 10 --endpoint bookings
  ```
* **Evaluation Checkpoint:** **Checkpoint 4 — Automated Workload Generation & Performance Evaluation**
* **Technical Description:**  
  Demonstrates terminal benchmark execution across 200 requests with 10 concurrent worker threads:
  * **Wall Clock Time:** 3.25 seconds
  * **Throughput:** 61.52 requests/second
  * **Success Rate:** 100.0% deterministic conflict handling
  * **Latency Percentiles:** $p50 = 99.52\text{ ms}$, $p90 = 128.74\text{ ms}$, $p95 = 184.08\text{ ms}$, $p99 = 1313.78\text{ ms}$
  * **Status Breakdown:** 200/200 requests returned `HTTP 409 Conflict`, verifying race-condition protection under high concurrency.

---

## Video Evidence: Dynamic Session Recording

* **File:** [`Recording 2026-10-05 115033.mp4`](Recording%202026-10-05%20115033.mp4)
* **Format:** MP4 Video (H.264 / AAC, 21.5 MB)
* **Description:** Continuous dynamic screen recording showing container bootup, API interactions, conflict handling, and live resource monitoring under Windows PowerShell.
