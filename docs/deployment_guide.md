# Deployment & Operations Guide

This guide covers running the **Movie & Concert Ticket Booking System** across three execution paradigms:
1. **Multi-Container Orchestration (Docker Compose) [Recommended]**
2. **Individual Docker Containers**
3. **Local Python Development Environment**

---

## 1. Prerequisites

- **Python:** 3.10 or higher
- **Docker:** Docker Engine 24.x+ / Docker Desktop
- **Docker Compose:** v2.x+
- **cURL or PowerShell** for API testing

---

## 2. Option 1: Multi-Container Deployment (Docker Compose)

This is the standard and fastest method to spin up the complete platform including all 5 microservices, the API Gateway, and container networking.

### Step 1: Clone or Navigate to the Project Root
```bash
cd C:\Users\Aditya\movie-concert-microservices
```

### Step 2: Build and Start All Containers in Background
```bash
docker compose up --build -d
```

### Step 3: Verify Running Services
```bash
docker compose ps
```
All 6 services will be displayed as `Up`:
- `api-gateway-container` (Port `8000:8000`)
- `event-service-container` (Port `5001:5000`)
- `user-service-container` (Port `5002:5000`)
- `seat-service-container` (Port `5003:5000`)
- `booking-service-container` (Port `5004:5000`)
- `payment-service-container` (Port `5005:5000`)

### Step 4: Verify Gateway Aggregated Health Check
```powershell
Invoke-RestMethod http://localhost:8000/health
```
or via cURL:
```bash
curl http://localhost:8000/health
```

### Step 5: Stop the Deployment
```bash
docker compose down
```

---

## 3. Option 2: Running Standalone Docker Containers

If running services individually without Compose:

### Step 1: Create the Dedicated Bridge Network
```bash
docker network create microservices-network
```

### Step 2: Build All Docker Images
```bash
docker build -t event-service:v1 ./services/event-service
docker build -t user-service:v1 ./services/user-service
docker build -t seat-service:v1 ./services/seat-service
docker build -t payment-service:v1 ./services/payment-service
docker build -t booking-service:v1 ./services/booking-service
docker build -t api-gateway:v1 ./api-gateway
```

### Step 3: Run the Containers on the Shared Network
```bash
docker run -d --name event-service-container --network microservices-network -p 5001:5000 event-service:v1
docker run -d --name user-service-container --network microservices-network -p 5002:5000 user-service:v1
docker run -d --name seat-service-container --network microservices-network -p 5003:5000 seat-service:v1
docker run -d --name payment-service-container --network microservices-network -p 5005:5000 payment-service:v1
docker run -d --name booking-service-container --network microservices-network -p 5004:5000 booking-service:v1
docker run -d --name api-gateway-container --network microservices-network -p 8000:8000 api-gateway:v1
```

---

## 4. Option 3: Local Python Execution (No Docker)

### Step 1: Install Dependencies
```bash
pip install flask requests
```

### Step 2: Launch Each Microservice in a Separate Terminal Window

**Terminal 1 (Event Service - Port 5001):**
```bash
cd services/event-service
python -c "from app import app; app.run(port=5001)"
```

**Terminal 2 (User Service - Port 5002):**
```bash
cd services/user-service
python -c "from app import app; app.run(port=5002)"
```

**Terminal 3 (Seat Service - Port 5003):**
```bash
cd services/seat-service
python -c "from app import app; app.run(port=5003)"
```

**Terminal 4 (Payment Service - Port 5005):**
```bash
cd services/payment-service
python -c "from app import app; app.run(port=5005)"
```

**Terminal 5 (Booking Service - Port 5004):**
```bash
cd services/booking-service
set USER_SERVICE_URL=http://localhost:5002
set EVENT_SERVICE_URL=http://localhost:5001
set SEAT_SERVICE_URL=http://localhost:5003
set PAYMENT_SERVICE_URL=http://localhost:5005
python -c "from app import app; app.run(port=5004)"
```

**Terminal 6 (API Gateway - Port 8000):**
```bash
cd api-gateway
set EVENT_SERVICE_URL=http://localhost:5001
set USER_SERVICE_URL=http://localhost:5002
set SEAT_SERVICE_URL=http://localhost:5003
set BOOKING_SERVICE_URL=http://localhost:5004
set PAYMENT_SERVICE_URL=http://localhost:5005
python app.py
```

---

## 5. Executing Load Tests & Benchmarks

Navigate to `load-testing/`:
```bash
cd load-testing
```

### 1. Run Baseline Load Test (100 Requests):
```bash
python load_generator.py -n 100 -c 10 --endpoint mix
```

### 2. Run Operational Load Test (1,000 Requests):
```bash
python load_generator.py -n 1000 -c 50 --endpoint mix
```

### 3. Run Stress Load Test (10,000 Requests):
```bash
python load_generator.py -n 10000 -c 100 --endpoint mix
```

### 4. Run Locust Interactive Web UI (Optional):
```bash
pip install locust
locust -f locustfile.py --host http://localhost:8000
```
Open your browser at `http://localhost:8089` to control simulated users.

### 5. Generate Performance Visualization Dashboard:
```bash
cd ../results
python generate_graphs.py
```
Open `results/dashboard.html` in your web browser to view the interactive visual graphs.
