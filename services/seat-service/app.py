from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory seat data
# Each event has its own set of seats.
seats = {
    1: {
        "A1": "available",
        "A2": "available",
        "A3": "available",
        "A4": "available",
        "A5": "available",
        "B1": "available",
        "B2": "available",
        "B3": "available",
        "B4": "available",
        "B5": "available"
    },
    2: {
        "A1": "available",
        "A2": "available",
        "A3": "available",
        "A4": "available",
        "A5": "available",
        "B1": "available",
        "B2": "available",
        "B3": "available",
        "B4": "available",
        "B5": "available"
    }
}


@app.route("/")
def home():
    return jsonify({
        "service": "Seat Service",
        "status": "running"
    })


@app.route("/seats/<int:event_id>", methods=["GET"])
def get_seats(event_id):
    if event_id not in seats:
        return jsonify({"error": "Event not found"}), 404

    return jsonify({
        "event_id": event_id,
        "seats": seats[event_id]
    })


@app.route("/seats/<int:event_id>/available", methods=["GET"])
def get_available_seats(event_id):
    if event_id not in seats:
        return jsonify({"error": "Event not found"}), 404

    available = [
        seat for seat, status in seats[event_id].items()
        if status == "available"
    ]

    return jsonify({
        "event_id": event_id,
        "available_seats": available
    })


@app.route("/seats/<int:event_id>/reserve", methods=["POST"])
def reserve_seats(event_id):
    if event_id not in seats:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json()

    if not data or "seats" not in data:
        return jsonify({"error": "Seats list is required"}), 400

    requested_seats = data["seats"]

    invalid_seats = [
        seat for seat in requested_seats
        if seat not in seats[event_id]
    ]

    if invalid_seats:
        return jsonify({
            "error": "Invalid seat(s)",
            "seats": invalid_seats
        }), 400

    unavailable_seats = [
        seat for seat in requested_seats
        if seats[event_id][seat] != "available"
    ]

    if unavailable_seats:
        return jsonify({
            "error": "Some seats are not available",
            "seats": unavailable_seats
        }), 409

    for seat in requested_seats:
        seats[event_id][seat] = "reserved"

    return jsonify({
        "message": "Seats reserved successfully",
        "event_id": event_id,
        "seats": requested_seats
    }), 200


@app.route("/seats/<int:event_id>/release", methods=["POST"])
def release_seats(event_id):
    if event_id not in seats:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json()

    if not data or "seats" not in data:
        return jsonify({"error": "Seats list is required"}), 400

    requested_seats = data["seats"]

    invalid_seats = [
        seat for seat in requested_seats
        if seat not in seats[event_id]
    ]

    if invalid_seats:
        return jsonify({
            "error": "Invalid seat(s)",
            "seats": invalid_seats
        }), 400

    for seat in requested_seats:
        seats[event_id][seat] = "available"

    return jsonify({
        "message": "Seats released successfully",
        "event_id": event_id,
        "seats": requested_seats
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)