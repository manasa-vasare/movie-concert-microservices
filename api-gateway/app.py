import os
import time
import requests
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Upstream microservice URLs with container defaults, configurable via environment
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service-container:5000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service-container:5000")
SEAT_SERVICE_URL = os.getenv("SEAT_SERVICE_URL", "http://seat-service-container:5000")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://booking-service-container:5000")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service-container:5000")

SERVICES = {
    "event_service": {
        "url": EVENT_SERVICE_URL,
        "description": "Event catalog and venue management"
    },
    "user_service": {
        "url": USER_SERVICE_URL,
        "description": "User profile and account management"
    },
    "seat_service": {
        "url": SEAT_SERVICE_URL,
        "description": "Seat availability, reservation, and releases"
    },
    "booking_service": {
        "url": BOOKING_SERVICE_URL,
        "description": "Booking workflow orchestration and history"
    },
    "payment_service": {
        "url": PAYMENT_SERVICE_URL,
        "description": "Payment processing and transaction auditing"
    }
}

HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailers", "transfer-encoding",
    "upgrade", "host", "content-length"
}


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


def forward_request(target_base_url, subpath):
    target_url = f"{target_base_url}/{subpath.lstrip('/')}"
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )

        response_headers = [
            (k, v) for k, v in resp.headers.items()
            if k.lower() not in HOP_BY_HOP_HEADERS
        ]

        return Response(resp.content, resp.status_code, response_headers)

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Upstream service timeout",
            "target": target_url
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Upstream service unavailable",
            "target": target_url
        }), 503
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Gateway forwarding error",
            "message": str(e)
        }), 502


@app.route("/")
def root():
    return jsonify({
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
        },
        "services": {k: v["url"] for k, v in SERVICES.items()}
    }), 200


@app.route("/health", methods=["GET"])
def health():
    summary = {
        "gateway": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    all_healthy = True

    for name, svc in SERVICES.items():
        t0 = time.time()
        try:
            r = requests.get(f"{svc['url']}/", timeout=3)
            latency_ms = round((time.time() - t0) * 1000, 2)
            if r.status_code == 200:
                summary["services"][name] = {
                    "status": "healthy",
                    "latency_ms": latency_ms
                }
            else:
                summary["services"][name] = {
                    "status": "degraded",
                    "code": r.status_code,
                    "latency_ms": latency_ms
                }
                all_healthy = False
        except Exception as e:
            summary["services"][name] = {
                "status": "unreachable",
                "error": str(e)
            }
            all_healthy = False

    status_code = 200 if all_healthy else 207
    return jsonify(summary), status_code


# ----------------------------------------------------
# Route Forwarding Rules
# ----------------------------------------------------

@app.route("/events", defaults={"subpath": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/events/<path:subpath>", methods=["GET", "POST", "OPTIONS"])
def route_events(subpath):
    if request.method == "OPTIONS":
        return Response("", status=204)
    full_path = f"events/{subpath}" if subpath else "events"
    return forward_request(EVENT_SERVICE_URL, full_path)


@app.route("/users", defaults={"subpath": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.route("/users/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def route_users(subpath):
    if request.method == "OPTIONS":
        return Response("", status=204)
    full_path = f"users/{subpath}" if subpath else "users"
    return forward_request(USER_SERVICE_URL, full_path)


@app.route("/seats", defaults={"subpath": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/seats/<path:subpath>", methods=["GET", "POST", "OPTIONS"])
def route_seats(subpath):
    if request.method == "OPTIONS":
        return Response("", status=204)
    full_path = f"seats/{subpath}" if subpath else "seats"
    return forward_request(SEAT_SERVICE_URL, full_path)


@app.route("/bookings", defaults={"subpath": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/bookings/<path:subpath>", methods=["GET", "POST", "OPTIONS"])
def route_bookings(subpath):
    if request.method == "OPTIONS":
        return Response("", status=204)
    full_path = f"bookings/{subpath}" if subpath else "bookings"
    return forward_request(BOOKING_SERVICE_URL, full_path)


@app.route("/payments", defaults={"subpath": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/payments/<path:subpath>", methods=["GET", "POST", "OPTIONS"])
def route_payments(subpath):
    if request.method == "OPTIONS":
        return Response("", status=204)
    full_path = f"payments/{subpath}" if subpath else "payments"
    return forward_request(PAYMENT_SERVICE_URL, full_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
