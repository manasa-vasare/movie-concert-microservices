from flask import Flask, jsonify, request
import requests
import uuid

app = Flask(__name__)

# Other microservices
USER_SERVICE_URL = "http://user-service-container:5000"
EVENT_SERVICE_URL = "http://event-service-container:5000"
SEAT_SERVICE_URL = "http://seat-service-container:5000"
PAYMENT_SERVICE_URL = "http://payment-service-container:5000"


@app.route("/")
def home():
    return jsonify({
        "service": "Booking Service",
        "status": "running"
    })


@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Booking data is required"
        }), 400

    required_fields = ["user_id", "event_id", "seats"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    user_id = data["user_id"]
    event_id = data["event_id"]
    requested_seats = data["seats"]

    if not requested_seats:
        return jsonify({
            "error": "At least one seat is required"
        }), 400

    # ------------------------------------------------
    # 1. Verify User
    # ------------------------------------------------
    try:
        user_response = requests.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            timeout=5
        )
    except requests.RequestException:
        return jsonify({
            "error": "User Service is unavailable"
        }), 503

    if user_response.status_code != 200:
        return jsonify({
            "error": "User not found"
        }), 404

    user = user_response.json()

    # ------------------------------------------------
    # 2. Verify Event
    # ------------------------------------------------
    try:
        event_response = requests.get(
            f"{EVENT_SERVICE_URL}/events/{event_id}",
            timeout=5
        )
    except requests.RequestException:
        return jsonify({
            "error": "Event Service is unavailable"
        }), 503

    if event_response.status_code != 200:
        return jsonify({
            "error": "Event not found"
        }), 404

    event = event_response.json()

    # ------------------------------------------------
    # 3. Reserve Seats
    # ------------------------------------------------
    try:
        seat_response = requests.post(
            f"{SEAT_SERVICE_URL}/seats/{event_id}/reserve",
            json={
                "seats": requested_seats
            },
            timeout=5
        )
    except requests.RequestException:
        return jsonify({
            "error": "Seat Service is unavailable"
        }), 503

    if seat_response.status_code != 200:
        return jsonify({
            "error": "Seat reservation failed",
            "details": seat_response.json()
        }), seat_response.status_code

    # ------------------------------------------------
    # 4. Calculate Amount
    # ------------------------------------------------
    seat_count = len(requested_seats)

    # Simple fixed ticket price for course project
    ticket_price = 500
    amount = seat_count * ticket_price

    # ------------------------------------------------
    # 5. Process Payment
    # ------------------------------------------------
    try:
        payment_response = requests.post(
            f"{PAYMENT_SERVICE_URL}/payments",
            json={
                "user_id": user_id,
                "amount": amount
            },
            timeout=5
        )
    except requests.RequestException:
        # Payment service unavailable.
        # Release the seats that were reserved.
        try:
            requests.post(
                f"{SEAT_SERVICE_URL}/seats/{event_id}/release",
                json={
                    "seats": requested_seats
                },
                timeout=5
            )
        except requests.RequestException:
            pass

        return jsonify({
            "error": "Payment Service is unavailable",
            "message": "Reserved seats were released"
        }), 503

    if payment_response.status_code != 200:
        # Payment failed, so release seats
        try:
            requests.post(
                f"{SEAT_SERVICE_URL}/seats/{event_id}/release",
                json={
                    "seats": requested_seats
                },
                timeout=5
            )
        except requests.RequestException:
            pass

        return jsonify({
            "error": "Payment failed",
            "details": payment_response.json(),
            "message": "Reserved seats were released"
        }), 400

    payment = payment_response.json()

    # ------------------------------------------------
    # 6. Create Booking
    # ------------------------------------------------
    booking_id = str(uuid.uuid4())

    return jsonify({
        "message": "Booking created successfully",
        "booking_id": booking_id,
        "user": user,
        "event": event,
        "seats": requested_seats,
        "amount": amount,
        "payment": payment,
        "status": "confirmed"
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)