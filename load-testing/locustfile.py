import random
from locust import HttpUser, task, between, tag


class TicketBookingUser(HttpUser):
    # Simulates realistic think time between user actions (0.5 to 2.5 seconds)
    wait_time = between(0.5, 2.5)

    def on_start(self):
        """Called when a virtual user starts running."""
        self.user_ids = [1, 2, 3]
        self.event_ids = [1, 2]
        self.all_seats = [f"{row}{num}" for row in ["A", "B"] for num in range(1, 6)]

    @tag('browse', 'events')
    @task(5)
    def browse_events(self):
        """Browse the full event catalog."""
        with self.client.get("/events", name="GET /events", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Failed to fetch events: HTTP {resp.status_code}")

    @tag('browse', 'events')
    @task(4)
    def view_single_event(self):
        """View specific event details."""
        event_id = random.choice(self.event_ids)
        with self.client.get(f"/events/{event_id}", name="GET /events/[id]", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Event {event_id} query failed: HTTP {resp.status_code}")

    @tag('browse', 'seats')
    @task(4)
    def check_available_seats(self):
        """Check seat availability for an event."""
        event_id = random.choice(self.event_ids)
        with self.client.get(f"/seats/{event_id}/available", name="GET /seats/[id]/available", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Seat query for event {event_id} failed: HTTP {resp.status_code}")

    @tag('users')
    @task(3)
    def view_user_profile(self):
        """Query user details."""
        user_id = random.choice(self.user_ids)
        with self.client.get(f"/users/{user_id}", name="GET /users/[id]", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"User {user_id} lookup failed: HTTP {resp.status_code}")

    @tag('health')
    @task(2)
    def check_gateway_health(self):
        """Query gateway and upstream microservices health."""
        with self.client.get("/health", name="GET /health", catch_response=True) as resp:
            if resp.status_code in (200, 207):
                resp.success()
            else:
                resp.failure(f"Health check degraded: HTTP {resp.status_code}")

    @tag('booking')
    @task(1)
    def attempt_booking(self):
        """Simulate an end-to-end booking transaction through the Gateway."""
        event_id = random.choice(self.event_ids)
        user_id = random.choice(self.user_ids)
        chosen_seat = random.choice(self.all_seats)

        payload = {
            "user_id": user_id,
            "event_id": event_id,
            "seats": [chosen_seat]
        }

        with self.client.post("/bookings", json=payload, name="POST /bookings", catch_response=True) as resp:
            # 201: Successfully booked
            # 409: Seat already reserved (expected under high concurrency)
            if resp.status_code in (201, 409):
                resp.success()
            else:
                resp.failure(f"Unexpected booking error: HTTP {resp.status_code} - {resp.text}")
