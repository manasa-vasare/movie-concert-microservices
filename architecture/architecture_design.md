# System Architecture & Design Document

**Project:** Movie & Concert Ticket Booking Platform  
**Course:** Cloud Computing Laboratory (CCLab)  
**Institution:** KLE Technological University  

---

## 1. High-Level Architecture

The system implements a domain-driven microservices architecture where client interactions pass through a single entry point—the **API Gateway**. Downstream services communicate synchronously via REST/HTTP over an isolated Docker bridge network.

```mermaid
flowchart TD
    Client["Web / Mobile / Load Generator"] -->|HTTP Requests| Gateway["API Gateway (Port 8000)"]
    Gateway -->|/events| EventSvc["Event Service (Port 5001)"]
    Gateway -->|/users| UserSvc["User Service (Port 5002)"]
    Gateway -->|/seats| SeatSvc["Seat Service (Port 5003)"]
    Gateway -->|/bookings| BookingSvc["Booking Service (Port 5004)"]
    Gateway -->|/payments| PaymentSvc["Payment Service (Port 5005)"]

    BookingSvc -.->|1. Verify User| UserSvc
    BookingSvc -.->|2. Verify Event| EventSvc
    BookingSvc -.->|3. Reserve Seats| SeatSvc
    BookingSvc -.->|4. Process Payment| PaymentSvc
    BookingSvc -.->|Rollback: Release Seats| SeatSvc
```

---

## 2. Microservice Domains & Port Allocation

| Component | Host Port | Container Port | Domain Responsibility |
| :--- | :---: | :---: | :--- |
| **API Gateway** | `8000` | `8000` | Reverse proxy, request forwarding, CORS, aggregated health checks |
| **Event Service** | `5001` | `5000` | Movie and concert catalog, venues, event dates |
| **User Service** | `5002` | `5000` | User account registrations and profile management |
| **Seat Service** | `5003` | `5000` | Seat inventory, real-time availability, reservation locks, seat releases |
| **Booking Service**| `5004` | `5000` | Orchestrates distributed booking transaction workflow |
| **Payment Service**| `5005` | `5000` | Transaction processing, payment validation, and receipt generation |

---

## 3. Distributed Booking Workflow & Compensation Pattern (Saga)

The **Booking Service** functions as an orchestrator implementing a lightweight Saga pattern with compensating actions to guarantee data consistency across microservices:

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant GW as API Gateway (8000)
    participant BK as Booking Service (5004)
    participant US as User Service (5002)
    participant EV as Event Service (5001)
    participant ST as Seat Service (5003)
    participant PY as Payment Service (5005)

    Client->>GW: POST /bookings {user_id, event_id, seats}
    GW->>BK: Forward POST /bookings
    BK->>US: GET /users/{user_id}
    US-->>BK: 200 OK (User Verified)
    BK->>EV: GET /events/{event_id}
    EV-->>BK: 200 OK (Event Verified)
    BK->>ST: POST /seats/{event_id}/reserve {seats}
    alt Seat Contention
        ST-->>BK: 409 Conflict (Seats Taken)
        BK-->>GW: 409 Conflict
        GW-->>Client: 409 Conflict
    else Seats Reserved
        ST-->>BK: 200 OK
        BK->>PY: POST /payments {user_id, amount}
        alt Payment Failure
            PY-->>BK: 400/500 Failed
            BK->>ST: POST /seats/{event_id}/release (Compensating Action)
            ST-->>BK: 200 OK
            BK-->>GW: 503 Payment Failed (Seats Released)
            GW-->>Client: 503 Service Error
        else Payment Succeeded
            PY-->>BK: 200 OK {transaction_id}
            BK-->>GW: 201 Created {booking_id, status: confirmed}
            GW-->>Client: 201 Created
        end
    end
```

---

## 4. Container Networking & Service Discovery

All microservices run in isolated containers attached to `microservices-network` (Docker bridge network). Inter-service communication relies on Docker's embedded DNS server, allowing services to resolve upstream dependencies by container name:
- `http://event-service-container:5000`
- `http://user-service-container:5000`
- `http://seat-service-container:5000`
- `http://booking-service-container:5000`
- `http://payment-service-container:5000`
