# API Documentation

**Base API Gateway Endpoint:** `http://localhost:8000`  
**Direct Service Endpoints:**
- Event Service: `http://localhost:5001`
- User Service: `http://localhost:5002`
- Seat Service: `http://localhost:5003`
- Booking Service: `http://localhost:5004`
- Payment Service: `http://localhost:5005`

---

## 1. API Gateway Endpoints

### 1.1 Gateway Information & Service Map
- **Method:** `GET`
- **Path:** `/`
- **Response:** `200 OK`
```json
{
  "gateway": "API Gateway",
  "version": "1.0.0",
  "status": "online",
  "description": "Unified Entry Point for Movie & Concert Ticket Booking Platform",
  "port": 8000,
  "routes": {
    "/events": "Event Service (Catalog)",
    "/users": "User Service (Profiles)",
    "/seats": "Seat Service (Inventory & Locks)",
    "/bookings": "Booking Service (Orchestration)",
    "/payments": "Payment Service (Transactions)",
    "/health": "Aggregated System Health Check"
  }
}
```

### 1.2 Aggregated System Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Response:** `200 OK`
```json
{
  "gateway": "healthy",
  "timestamp": 1728000000.0,
  "services": {
    "booking_service": { "latency_ms": 3.42, "status": "healthy" },
    "event_service": { "latency_ms": 1.12, "status": "healthy" },
    "payment_service": { "latency_ms": 1.84, "status": "healthy" },
    "seat_service": { "latency_ms": 1.55, "status": "healthy" },
    "user_service": { "latency_ms": 1.21, "status": "healthy" }
  }
}
```

---

## 2. Event Endpoints (via Gateway `/events` or Service Port `5001`)

### 2.1 Get All Events
- **Method:** `GET`
- **Path:** `/events`
```bash
curl http://localhost:8000/events
```
- **Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Avengers: Secret Wars",
    "type": "movie",
    "venue": "PVR Hubli",
    "date": "2026-10-05"
  },
  {
    "id": 2,
    "name": "Arijit Singh Live",
    "type": "concert",
    "venue": "Bengaluru",
    "date": "2026-10-10"
  }
]
```

### 2.2 Get Event by ID
- **Method:** `GET`
- **Path:** `/events/1`
- **Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Avengers: Secret Wars",
  "type": "movie",
  "venue": "PVR Hubli",
  "date": "2026-10-05"
}
```

---

## 3. User Endpoints (via Gateway `/users` or Service Port `5002`)

### 3.1 Get All Users
- **Method:** `GET`
- **Path:** `/users`
```json
[
  { "id": 1, "name": "Manasa", "email": "manasa@example.com" },
  { "id": 2, "name": "Renuka", "email": "renuka@test.conm" },
  { "id": 3, "name": "Aditya", "email": "aditya@test.conm" }
]
```

### 3.2 Create User
- **Method:** `POST`
- **Path:** `/users`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "name": "Bruce Wayne",
  "email": "bruce@waynecorp.com"
}
```
- **Response:** `201 Created`
```json
{
  "id": 4,
  "name": "Bruce Wayne",
  "email": "bruce@waynecorp.com"
}
```

---

## 4. Seat Endpoints (via Gateway `/seats` or Service Port `5003`)

### 4.1 Get Available Seats
- **Method:** `GET`
- **Path:** `/seats/1/available`
- **Response:** `200 OK`
```json
{
  "event_id": 1,
  "available_seats": ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5"]
}
```

### 4.2 Reserve Seats
- **Method:** `POST`
- **Path:** `/seats/1/reserve`
- **Request Body:**
```json
{
  "seats": ["A1", "A2"]
}
```
- **Response:** `200 OK`
```json
{
  "message": "Seats reserved successfully",
  "event_id": 1,
  "seats": ["A1", "A2"]
}
```
- **Conflict Error:** `409 Conflict` (if already reserved)
```json
{
  "error": "Some seats are not available",
  "seats": ["A1"]
}
```

---

## 5. Booking Endpoints (via Gateway `/bookings` or Service Port `5004`)

### 5.1 Create Distributed Booking (End-to-End Orchestration)
- **Method:** `POST`
- **Path:** `/bookings`
- **Request Body:**
```json
{
  "user_id": 3,
  "event_id": 1,
  "seats": ["A3", "A4"]
}
```
- **Response:** `201 Created`
```json
{
  "message": "Booking created successfully",
  "booking_id": "8fbb121d-9db2-4874-a6c3-181f721dcfc1",
  "user": {
    "id": 3,
    "name": "Aditya",
    "email": "aditya@test.conm"
  },
  "event": {
    "id": 1,
    "name": "Avengers: Secret Wars",
    "type": "movie",
    "venue": "PVR Hubli",
    "date": "2026-10-05"
  },
  "seats": ["A3", "A4"],
  "amount": 1000,
  "payment": {
    "message": "Payment successful",
    "transaction_id": "76ec965b-7b02-4fc7-8cb5-e4070a7bbbc9",
    "user_id": 3,
    "amount": 1000.0,
    "status": "completed"
  },
  "status": "confirmed"
}
```

---

## 6. Payment Endpoints (via Gateway `/payments` or Service Port `5005`)

### 6.1 Process Payment Directly
- **Method:** `POST`
- **Path:** `/payments`
- **Request Body:**
```json
{
  "user_id": 3,
  "amount": 500
}
```
- **Response:** `200 OK`
```json
{
  "message": "Payment successful",
  "transaction_id": "cb17d91e-f3f8-4e8c-a1c6-11f848bece31",
  "user_id": 3,
  "amount": 500.0,
  "status": "completed"
}
```
