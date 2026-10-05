# Movie & Concert Ticket Booking System

A containerized, microservices-based ticket booking platform designed for movies and live concert events. This project demonstrates microservice design principles, RESTful inter-service communication, containerization with Docker, multi-container orchestration with Docker Compose, API Gateway reverse-proxy routing, and rigorous performance benchmarking under varying load conditions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Microservices Breakdown](#microservices-breakdown)
- [Repository Structure](#repository-structure)
- [Service Specifications](#service-specifications)
  - [API Gateway](#api-gateway)
  - [Event Service](#event-service)
  - [User Service](#user-service)
  - [Seat Service](#seat-service)
  - [Booking Service](#booking-service)
  - [Payment Service](#payment-service)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Multi-Container Deployment (Docker Compose)](#multi-container-deployment-docker-compose)
  - [Running Individual Services](#running-individual-services)
- [API Testing & Verification](#api-testing--verification)
- [Load Testing & Performance Evaluation](#load-testing--performance-evaluation)
- [Project Roadmap](#project-roadmap)
- [Academic Context & Team Contributions](#academic-context--team-contributions)

---

## Project Overview

The **Movie & Concert Ticket Booking System** decouples traditional monolithic ticketing operations into autonomous, loosely-coupled microservices. Each service encapsulates a distinct business domain with its own code, dependencies, and deployment lifecycle.

### Key Objectives

- **Domain-Driven Isolation:** Independent microservices for Users, Events, Seats, Bookings, and Payments.
- **Unified Entry Point:** API Gateway acting as a reverse proxy, insulating backend services from clients.
- **Containerization:** Each service packages its own runtime environment using lightweight Docker containers (`python:3.12-slim`).
- **Standardized REST Communication:** Clear HTTP/JSON communication contracts between services.
- **Scalability & Orchestration:** Fully orchestrated with Docker Compose on an isolated bridge network (`microservices-network`).
- **Distributed Transaction Reliability:** Saga orchestration pattern in the Booking Service with compensating releases upon payment failure.
- **Performance Evaluation:** Multi-tier load testing (100, 1,000, 10,000 requests) using Locust and a custom multi-threaded Python load generator.

---

## System Architecture

```text
                           +------------------+
                           |      Client      |
                           |  Web / Mobile    |
                           +--------+---------+
                                    |
                                    | HTTP / REST
                                    v
                           +------------------+
                           |   API Gateway    |
                           |    Port 8000     |
                           +--------+---------+
                                    |
              +---------------------+----------------------+
              |                     |                      |
              v                     v                      v
       +--------------+      +--------------+      +--------------+
       | User Service |      | Event Service|      | Seat Service |
       |   Port 5002  |      |   Port 5001  |      |   Port 5003  |
       +--------------+      +--------------+      +------+-------+
                                                          |
                                                          v
                                                   +--------------+
                                                   |Booking Service|
                                                   |   Port 5004  |
                                                   +------+-------+
                                                          |
                                                          v
                                                   +--------------+
                                                   |Payment Service|
                                                   |   Port 5005  |
                                                   +--------------+
```

### Booking Service Orchestration Flow

```text
Client -> API Gateway (Port 8000)
             |
             v
       Booking Service (Port 5004)
             |
             +----> User Service (Port 5002): Verify User Exists
             |
             +----> Event Service (Port 5001): Verify Event Exists
             |
             +----> Seat Service (Port 5003): Reserve Seats (HTTP 409 if contested)
             |
             +----> Payment Service (Port 5005): Process Payment
             |        |
             |        +--> [Success]: Booking Confirmed (HTTP 201)
             |        +--> [Failure]: Compensating Release of Seats (HTTP 503)
             v
       Confirmed Booking Receipt
```

---

## Microservices Breakdown

| Service | Host Port | Container Port | Description | Status |
| :--- | :---: | :---: | :--- | :---: |
| **API Gateway** | `8000` | `8000` | Unified entry point, request proxying, CORS & health monitoring | **Active** |
| **Event Service** | `5001` | `5000` | Manages movie and concert event catalog and venues | **Active** |
| **User Service** | `5002` | `5000` | Manages users and user profiles | **Active** |
| **Seat Service** | `5003` | `5000` | Manages real-time seat inventory, locks, and releases | **Active** |
| **Booking Service** | `5004` | `5000` | Coordinates end-to-end distributed booking workflow | **Active** |
| **Payment Service** | `5005` | `5000` | Processes payments and generates transaction audits | **Active** |

---

## Repository Structure

```text
movie-concert-microservices/
│
├── api-gateway/
│   ├── app.py                      # Reverse proxy & request router
│   ├── requirements.txt            # Gateway dependencies (Flask, requests)
│   └── Dockerfile                  # Gateway container spec (Port 8000)
│
├── architecture/
│   └── architecture_design.md      # Architecture diagrams & sequence workflows
│
├── docs/
│   ├── api_documentation.md        # Comprehensive endpoint contracts & samples
│   └── deployment_guide.md         # Local & Docker deployment instructions
│
├── load-testing/
│   ├── locustfile.py               # Locust load test suite
│   └── load_generator.py           # Custom multi-threaded benchmark generator
│
├── results/
│   ├── benchmark_summary.json      # Structured load test metrics (100, 1K, 10K)
│   ├── benchmark_report.md         # Full academic evaluation report
│   ├── generate_graphs.py          # Dashboard & chart generator
│   └── dashboard.html              # Interactive performance report
│
├── services/
│   ├── event-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── user-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── seat-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── booking-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── payment-service/
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── docker-compose.yml              # Complete 6-service orchestration
├── .gitignore
└── README.md
```

---

## Service Specifications

### API Gateway

The API Gateway is the public reverse proxy routing incoming traffic to appropriate internal services and aggregating overall system health.

- **Base URL:** `http://localhost:8000`
- **Container Port:** `8000`
- **Host Port:** `8000`

#### Available Routes

| Method | Route | Target Backend | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Gateway | Gateway metadata & registered service endpoints |
| `GET` | `/health` | All Services | Aggregated live health check and latency ping |
| `ALL` | `/events/*` | Event Service | Event catalog queries |
| `ALL` | `/users/*` | User Service | User accounts and profile actions |
| `ALL` | `/seats/*` | Seat Service | Seat availability, reservation, release |
| `ALL` | `/bookings/*` | Booking Service| End-to-end booking orchestration |
| `ALL` | `/payments/*`| Payment Service| Payment transactions |

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- [Python 3.10+](https://www.python.org/)

### Multi-Container Deployment (Docker Compose)

From the project root directory, spin up all 6 microservices with a single command:

```bash
docker compose up --build -d
```

Verify that all 6 containers are running:
```bash
docker compose ps
```

Verify the complete system health via the API Gateway:
```powershell
Invoke-RestMethod http://localhost:8000/health
```

To stop all containers:
```bash
docker compose down
```

---

## API Testing & Verification

### 1. Test Gateway Health
```powershell
Invoke-RestMethod http://localhost:8000/health
```

### 2. Browse Events (via Gateway)
```powershell
Invoke-RestMethod http://localhost:8000/events
```

### 3. Check Available Seats (via Gateway)
```powershell
Invoke-RestMethod http://localhost:8000/seats/1/available
```

### 4. Create an End-to-End Booking (via Gateway)
```powershell
$body = @{
    user_id = 3
    event_id = 1
    seats = @("A1", "A2")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/bookings" -Method Post -Body $body -ContentType "application/json"
```

---

## Load Testing & Performance Evaluation

The platform was evaluated under three discrete workload tiers (100, 1,000, and 10,000 requests) using the custom benchmark generator (`load-testing/load_generator.py`).

### Performance Summary Table

| Metric | 100 Users | 1,000 Users | 10,000 Users |
| :--- | :---: | :---: | :---: |
| **Concurrency** | 10 Threads | 50 Threads | 100 Threads |
| **Throughput (RPS)** | **411.52 RPS** | **845.31 RPS** | **1,120.07 RPS** |
| **Median Latency ($p50$)** | 18.20 ms | 46.10 ms | 76.50 ms |
| **90th Percentile ($p90$)** | 31.50 ms | 89.20 ms | 142.00 ms |
| **99th Percentile ($p99$)** | 68.30 ms | 165.80 ms | 284.10 ms |
| **Failure Rate** | 0.00% | 0.00% | 0.20% |

### Lab Evaluation Hardware Observation Table (1-16 Concurrency)

Recorded using `docker stats` during live evaluation workloads:

| Workload | Concurrency | Peak CPU (%) | Peak Memory (MiB) | Throughput (RPS) | p50 Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **W1** | 1 | 25.31% | 26.45 MiB | 120 | 10.0 |
| **W2** | 2 | 74.60% | 26.65 MiB | 250 | 14.0 |
| **W3** | 4 | 133.31% | 27.67 MiB | 411 | 18.20 |
| **W4** | 8 | 147.50% | 27.97 MiB | 650 | 30.0 |
| **W5** | 16 | 149.34% | 28.33 MiB | 845 | 46.10 |

### Running the Custom Load Generator

```bash
cd load-testing
python load_generator.py -n 1000 -c 50 --endpoint mix
```

### Viewing the Performance Dashboard

Generate the visualization graphs and open the interactive dashboard:
```bash
cd results
python generate_graphs.py
# Open results/dashboard.html in any browser
```

---

## Project Roadmap

- [x] **Milestone 1:** Architecture & domain modeling
- [x] **Milestone 2:** Implement & containerize Event Service
- [x] **Milestone 3:** Implement & containerize User Service
- [x] **Milestone 4:** Implement & containerize Seat Service
- [x] **Milestone 5:** Implement & containerize Payment Service
- [x] **Milestone 5:** Implement & containerize Booking Service
- [x] **Milestone 6:** Implement & configure unified API Gateway
- [x] **Milestone 6:** Complete Docker Compose multi-container orchestration
- [x] **Milestone 7:** Build Locust load testing suite (`locustfile.py`)
- [x] **Milestone 7:** Build custom multi-threaded Python load generator (`load_generator.py`)
- [x] **Milestone 7:** Generate performance charts, dashboard, and benchmark evaluation report

---

## Academic Context & Team Contributions

- **Course:** Cloud Computing Laboratory (CCLab) — Semester 5
- **Institution:** KLE Technological University
- **Project:** Movie & Concert Ticket Booking System

### Team Contributions Breakdown

| Team Member | Components Implemented |
| :--- | :--- |
| **Manasa** | Event Service, User Service, Initial Base Architecture |
| **Renuka** | Seat Service, Payment Service, Booking Service Orchestration |
| **Aditya** | **API Gateway (Port 8000)**, **Docker Compose Multi-Container Orchestration**, **Load Testing Suite (Locust & Custom Load Generator)**, **Performance Benchmarking (100, 1K, 10K Workloads)**, **Visualization Dashboard & Benchmark Report** |
