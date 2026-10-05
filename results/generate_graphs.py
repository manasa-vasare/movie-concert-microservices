#!/usr/bin/env python3
"""
Performance Visualization and Report Generator
Designed for KLE Technological University - Cloud Computing Laboratory (CCLab)
Author: Aditya
"""

import json
import os
import sys

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(RESULTS_DIR, "benchmark_summary.json")


def generate_html_report(data):
    """Generate a clean self-contained HTML dashboard with charts."""
    benchmarks = data.get("benchmarks", [])
    workloads = [b["workload"].replace("_", " ").title() for b in benchmarks]
    throughputs = [b["throughput_rps"] for b in benchmarks]
    p50_latencies = [b["latencies_ms"]["p50"] for b in benchmarks]
    p90_latencies = [b["latencies_ms"]["p90"] for b in benchmarks]
    p95_latencies = [b["latencies_ms"]["p95"] for b in benchmarks]
    p99_latencies = [b["latencies_ms"]["p99"] for b in benchmarks]
    error_rates = [b["failure_rate_percent"] for b in benchmarks]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Benchmark Report - Movie & Concert Microservices</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }}
        .card h2 {{
            margin-top: 0;
            font-size: 18px;
            color: #334155;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background-color: #f8fafc;
            font-weight: 600;
            color: #475569;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background-color: #dcfce7; color: #15803d; }}
        .badge-info {{ background-color: #e0f2fe; color: #0369a1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Movie & Concert Ticket Booking Platform</h1>
            <p>Cloud Computing Laboratory (CCLab) | Microservices Performance Evaluation Dashboard</p>
        </div>

        <div class="card-grid">
            <div class="card">
                <h2>Throughput vs Workload (RPS)</h2>
                <canvas id="throughputChart"></canvas>
            </div>
            <div class="card">
                <h2>Latency Percentiles (p50, p90, p95, p99) ms</h2>
                <canvas id="latencyChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>Detailed Benchmark Metrics Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Workload</th>
                        <th>Concurrency</th>
                        <th>Total Requests</th>
                        <th>Throughput (RPS)</th>
                        <th>p50 Latency</th>
                        <th>p90 Latency</th>
                        <th>p99 Latency</th>
                        <th>Failure Rate</th>
                    </tr>
                </thead>
                <tbody>
"""

    for b in benchmarks:
        name = b["workload"].replace("_", " ").title()
        html_content += f"""                    <tr>
                        <td><strong>{name}</strong></td>
                        <td>{b['concurrency']} threads</td>
                        <td>{b['total_requests']:,}</td>
                        <td><span class="badge badge-info">{b['throughput_rps']} RPS</span></td>
                        <td>{b['latencies_ms']['p50']} ms</td>
                        <td>{b['latencies_ms']['p90']} ms</td>
                        <td>{b['latencies_ms']['p99']} ms</td>
                        <td><span class="badge badge-success">{b['failure_rate_percent']}%</span></td>
                    </tr>
"""

    html_content += f"""                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctxThroughput = document.getElementById('throughputChart').getContext('2d');
        new Chart(ctxThroughput, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(workloads)},
                datasets: [{{
                    label: 'Requests Per Second (RPS)',
                    data: {json.dumps(throughputs)},
                    backgroundColor: ['#60a5fa', '#3b82f6', '#1d4ed8'],
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'RPS' }} }}
                }}
            }}
        }});

        const ctxLatency = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctxLatency, {{
            type: 'line',
            data: {{
                labels: {json.dumps(workloads)},
                datasets: [
                    {{ label: 'p50 (Median)', data: {json.dumps(p50_latencies)}, borderColor: '#10b981', fill: false, tension: 0.1 }},
                    {{ label: 'p90', data: {json.dumps(p90_latencies)}, borderColor: '#3b82f6', fill: false, tension: 0.1 }},
                    {{ label: 'p95', data: {json.dumps(p95_latencies)}, borderColor: '#f59e0b', fill: false, tension: 0.1 }},
                    {{ label: 'p99', data: {json.dumps(p99_latencies)}, borderColor: '#ef4444', fill: false, tension: 0.1 }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Milliseconds' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    html_file = os.path.join(RESULTS_DIR, "dashboard.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated interactive benchmark dashboard: {html_file}")


def generate_matplotlib_charts(data):
    """Generate static PNG charts if matplotlib is installed."""
    try:
        import matplotlib.pyplot as plt
        benchmarks = data.get("benchmarks", [])
        workloads = [b["workload"].replace("_", " ").title() for b in benchmarks]
        throughputs = [b["throughput_rps"] for b in benchmarks]

        # 1. Throughput Chart
        plt.figure(figsize=(8, 5))
        plt.bar(workloads, throughputs, color=["#60a5fa", "#3b82f6", "#1d4ed8"])
        plt.title("Microservices Platform Throughput (RPS)")
        plt.xlabel("Workload Profile")
        plt.ylabel("Requests Per Second (RPS)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        chart_path = os.path.join(RESULTS_DIR, "throughput_comparison.png")
        plt.savefig(chart_path, dpi=300)
        plt.close()
        print(f"Generated static chart: {chart_path}")

        # 2. Latency Percentiles Chart
        plt.figure(figsize=(9, 5))
        p50 = [b["latencies_ms"]["p50"] for b in benchmarks]
        p90 = [b["latencies_ms"]["p90"] for b in benchmarks]
        p95 = [b["latencies_ms"]["p95"] for b in benchmarks]
        p99 = [b["latencies_ms"]["p99"] for b in benchmarks]

        plt.plot(workloads, p50, marker='o', label='p50 (Median)', color='#10b981', linewidth=2)
        plt.plot(workloads, p90, marker='s', label='p90', color='#3b82f6', linewidth=2)
        plt.plot(workloads, p95, marker='^', label='p95', color='#f59e0b', linewidth=2)
        plt.plot(workloads, p99, marker='d', label='p99', color='#ef4444', linewidth=2)

        plt.title("Response Time Percentiles Across Workloads")
        plt.xlabel("Workload Profile")
        plt.ylabel("Latency (Milliseconds)")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        lat_path = os.path.join(RESULTS_DIR, "latency_percentiles.png")
        plt.savefig(lat_path, dpi=300)
        plt.close()
        print(f"Generated static chart: {lat_path}")

    except ImportError:
        print("Note: matplotlib not found; generated HTML dashboard instead.")


def main():
    if not os.path.exists(SUMMARY_FILE):
        print(f"Error: {SUMMARY_FILE} not found.")
        sys.exit(1)

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    generate_html_report(data)
    generate_matplotlib_charts(data)


if __name__ == "__main__":
    main()
