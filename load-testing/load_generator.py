#!/usr/bin/env python3
"""
High-Performance Custom Load Generator for Microservices Benchmarking
Designed for KLE Technological University - Cloud Computing Laboratory (CCLab)
Author: Aditya
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Benchmark Movie & Concert Ticket Booking Microservices Platform"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="http://localhost:8000",
        help="Base URL of API Gateway or service (default: http://localhost:8000)"
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=20,
        help="Number of concurrent worker threads (default: 20)"
    )
    parser.add_argument(
        "-n", "--requests",
        type=int,
        default=1000,
        help="Total number of requests to execute (e.g., 100, 1000, 10000; default: 1000)"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="mix",
        choices=["mix", "events", "seats", "users", "bookings", "health"],
        help="Target endpoint or 'mix' for realistic e-commerce traffic mix (default: mix)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../results/benchmark_summary.json",
        help="File path to save the JSON benchmark results"
    )
    return parser.parse_args()


def generate_request(base_url, endpoint_mode):
    """Generate target URL, HTTP method, and JSON body depending on endpoint mode."""
    all_seats = [f"{row}{num}" for row in ["A", "B"] for num in range(1, 6)]

    if endpoint_mode == "events":
        return f"{base_url}/events", "GET", None
    elif endpoint_mode == "seats":
        return f"{base_url}/seats/1/available", "GET", None
    elif endpoint_mode == "users":
        return f"{base_url}/users/1", "GET", None
    elif endpoint_mode == "health":
        return f"{base_url}/health", "GET", None
    elif endpoint_mode == "bookings":
        payload = {
            "user_id": random.choice([1, 2, 3]),
            "event_id": random.choice([1, 2]),
            "seats": [random.choice(all_seats)]
        }
        return f"{base_url}/bookings", "POST", payload
    else:
        # Realistic traffic distribution:
        # 50% browse events, 25% check seats, 15% user lookup, 10% bookings
        dice = random.random()
        if dice < 0.50:
            return f"{base_url}/events", "GET", None
        elif dice < 0.75:
            return f"{base_url}/seats/1/available", "GET", None
        elif dice < 0.90:
            return f"{base_url}/users/{random.choice([1, 2, 3])}", "GET", None
        else:
            payload = {
                "user_id": random.choice([1, 2, 3]),
                "event_id": random.choice([1, 2]),
                "seats": [random.choice(all_seats)]
            }
            return f"{base_url}/bookings", "POST", payload


def send_single_request(url, method, payload):
    """Execute a single HTTP request and record exact response latency."""
    t_start = time.perf_counter()
    headers = {"Content-Type": "application/json"}
    data_bytes = json.dumps(payload).encode("utf-8") if payload else None

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            latency = (time.perf_counter() - t_start) * 1000.0
            return {
                "status_code": response.status,
                "latency_ms": latency,
                "success": True,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        # 409 Conflict for already-reserved seat is an expected business outcome during booking contention
        is_success = (e.code == 409 and "/bookings" in url)
        return {
            "status_code": e.code,
            "latency_ms": latency,
            "success": is_success,
            "error": f"HTTP {e.code}"
        }
    except Exception as ex:
        latency = (time.perf_counter() - t_start) * 1000.0
        return {
            "status_code": 0,
            "latency_ms": latency,
            "success": False,
            "error": str(ex)
        }


def calculate_percentile(sorted_list, percentile):
    if not sorted_list:
        return 0.0
    k = (len(sorted_list) - 1) * (percentile / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_list) - 1)
    d = k - f
    return sorted_list[f] + d * (sorted_list[c] - sorted_list[f])


def run_benchmark(target_url, concurrency, total_requests, endpoint_mode):
    print("=" * 70)
    print("   MOVIE & CONCERT MICROSERVICES - BENCHMARK LOAD GENERATOR")
    print("=" * 70)
    print(f"Target Gateway URL : {target_url}")
    print(f"Workload Mode      : {endpoint_mode}")
    print(f"Concurrent Workers : {concurrency}")
    print(f"Total Requests     : {total_requests}")
    print("-" * 70)
    print("Starting load generation, please wait...")

    results = []
    wall_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for _ in range(total_requests):
            url, method, payload = generate_request(target_url, endpoint_mode)
            futures.append(executor.submit(send_single_request, url, method, payload))

        completed = 0
        for f in as_completed(futures):
            res = f.result()
            results.append(res)
            completed += 1
            if completed % max(1, total_requests // 10) == 0 or completed == total_requests:
                pct = int((completed / total_requests) * 100)
                sys.stdout.write(f"\rProgress: [{('=' * (pct // 5)):<20}] {pct}% ({completed}/{total_requests})")
                sys.stdout.flush()

    wall_duration = time.perf_counter() - wall_start
    print("\nBenchmark completed successfully!\n")

    # Analyze metrics
    latencies = sorted([r["latency_ms"] for r in results])
    success_count = sum(1 for r in results if r["success"])
    failure_count = total_requests - success_count
    status_distribution = {}
    for r in results:
        code = r["status_code"]
        status_distribution[code] = status_distribution.get(code, 0) + 1

    throughput = total_requests / wall_duration if wall_duration > 0 else 0
    failure_rate = (failure_count / total_requests) * 100.0

    p50 = calculate_percentile(latencies, 50)
    p90 = calculate_percentile(latencies, 90)
    p95 = calculate_percentile(latencies, 95)
    p99 = calculate_percentile(latencies, 99)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    min_latency = latencies[0] if latencies else 0.0
    max_latency = latencies[-1] if latencies else 0.0

    metrics = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": target_url,
        "endpoint_mode": endpoint_mode,
        "concurrency": concurrency,
        "total_requests": total_requests,
        "duration_seconds": round(wall_duration, 3),
        "throughput_rps": round(throughput, 2),
        "successful_requests": success_count,
        "failed_requests": failure_count,
        "failure_rate_percent": round(failure_rate, 2),
        "latencies_ms": {
            "min": round(min_latency, 2),
            "avg": round(avg_latency, 2),
            "max": round(max_latency, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2)
        },
        "status_distribution": status_distribution
    }

    # Print summary
    print("=" * 70)
    print("                    PERFORMANCE EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Wall Clock Time    : {wall_duration:.2f} seconds")
    print(f"Throughput (RPS)   : {throughput:.2f} requests/sec")
    print(f"Successful Requests: {success_count} ({100 - failure_rate:.1f}%)")
    print(f"Failed Requests    : {failure_count} ({failure_rate:.1f}%)")
    print("-" * 70)
    print("Response Time Percentiles (Latency):")
    print(f"  * Min Latency    : {min_latency:.2f} ms")
    print(f"  * Average Latency: {avg_latency:.2f} ms")
    print(f"  * Median (50th)  : {p50:.2f} ms")
    print(f"  * 90th Percentile: {p90:.2f} ms")
    print(f"  * 95th Percentile: {p95:.2f} ms")
    print(f"  * 99th Percentile: {p99:.2f} ms")
    print(f"  * Max Latency    : {max_latency:.2f} ms")
    print("-" * 70)
    print("HTTP Status Code Breakdown:")
    for code, count in sorted(status_distribution.items()):
        label = "Connection Error" if code == 0 else f"HTTP {code}"
        print(f"  * {label:<16}: {count} ({count / total_requests * 100:.1f}%)")
    print("=" * 70)

    return metrics


def main():
    args = parse_arguments()
    metrics = run_benchmark(
        target_url=args.target,
        concurrency=args.concurrency,
        total_requests=args.requests,
        endpoint_mode=args.endpoint
    )

    output_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print(f"Detailed benchmark metrics exported to: {args.output}")


if __name__ == "__main__":
    main()
