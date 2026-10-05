#!/usr/bin/env python3
"""
Performance Visualization and Report Generator
Designed for KLE Technological University - Cloud Computing Laboratory (CCLab)
Author: Aditya Rajashekhar Gavimath
"""

import json
import os
import sys

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(RESULTS_DIR, "benchmark_summary.json")


def generate_publication_quality_charts(data):
    """Generate high-resolution, clear, professional charts matching lab manual requirements."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np

        benchmarks = data.get("benchmarks", [])
        if not benchmarks:
            print("Error: No benchmark data found in JSON.")
            return

        workloads = [b["workload"] for b in benchmarks]
        throughputs = [b["throughput_rps"] for b in benchmarks]
        concurrency = [b["concurrency"] for b in benchmarks]

        p50 = [b["latencies_ms"]["p50"] for b in benchmarks]
        p90 = [b["latencies_ms"]["p90"] for b in benchmarks]
        p95 = [b["latencies_ms"]["p95"] for b in benchmarks]
        p99 = [b["latencies_ms"]["p99"] for b in benchmarks]
        avgs = [b["latencies_ms"]["avg"] for b in benchmarks]

        # -------------------------------------------------------------
        # Chart 1: Throughput Comparison Bar Chart (with exact data labels)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
        bars = ax.bar(workloads, throughputs, color=['#2563eb', '#0284c7', '#0d9488'], width=0.55, edgecolor='#1e293b', linewidth=1.2)

        ax.set_title("Microservices Platform Throughput Scaling (Requests Per Second)", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel("Workload Evaluation Profile", fontsize=11, fontweight='semibold', labelpad=10, color='#1e293b')
        ax.set_ylabel("Throughput (RPS)", fontsize=11, fontweight='semibold', labelpad=10, color='#1e293b')
        ax.set_ylim(0, max(throughputs) * 1.22)
        ax.grid(axis='y', linestyle='--', alpha=0.6, color='#94a3b8')
        ax.set_axisbelow(True)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f} RPS',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 6),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0f172a')

        plt.tight_layout()
        throughput_file = os.path.join(RESULTS_DIR, "throughput_comparison.png")
        plt.savefig(throughput_file, dpi=300)
        plt.close()
        print(f"Generated high-resolution chart: {throughput_file}")

        # -------------------------------------------------------------
        # Chart 2: Latency Percentiles Multi-Line Chart (p50, p90, p95, p99)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.plot(workloads, p50, marker='o', markersize=8, label='p50 (Median)', color='#10b981', linewidth=2.4)
        ax.plot(workloads, p90, marker='s', markersize=8, label='p90 (90th percentile)', color='#0284c7', linewidth=2.4)
        ax.plot(workloads, p95, marker='^', markersize=8, label='p95 (95th percentile)', color='#f59e0b', linewidth=2.4)
        ax.plot(workloads, p99, marker='D', markersize=8, label='p99 (99th percentile)', color='#ef4444', linewidth=2.4)

        ax.set_title("Response Time Percentiles Across Workloads (Latency in ms)", fontsize=13, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel("Workload Evaluation Profile", fontsize=11, fontweight='semibold', labelpad=10, color='#1e293b')
        ax.set_ylabel("Latency (Milliseconds)", fontsize=11, fontweight='semibold', labelpad=10, color='#1e293b')
        ax.grid(True, linestyle='--', alpha=0.6, color='#94a3b8')
        ax.set_axisbelow(True)
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)

        # Annotate points
        for i, txt in enumerate(p50):
            ax.annotate(f"{txt:.1f}ms", (workloads[i], p50[i]), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, fontweight='bold', color='#047857')
        for i, txt in enumerate(p99):
            ax.annotate(f"{txt:.1f}ms", (workloads[i], p99[i]), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, fontweight='bold', color='#b91c1c')

        plt.tight_layout()
        latency_file = os.path.join(RESULTS_DIR, "latency_percentiles.png")
        plt.savefig(latency_file, dpi=300)
        plt.close()
        print(f"Generated high-resolution chart: {latency_file}")

        # -------------------------------------------------------------
        # Chart 3: Concurrency Scaling Curve (Throughput vs Concurrency)
        # -------------------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)

        color = '#2563eb'
        ax1.set_xlabel('Concurrency Level (Virtual Worker Threads)', fontsize=11, fontweight='semibold', labelpad=10)
        ax1.set_ylabel('Throughput (RPS)', color=color, fontsize=11, fontweight='semibold', labelpad=10)
        line1 = ax1.plot(concurrency, throughputs, marker='o', markersize=8, color=color, linewidth=2.5, label='Throughput (RPS)')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle='--', alpha=0.5)

        ax2 = ax1.twinx()
        color = '#dc2626'
        ax2.set_ylabel('Average Latency (ms)', color=color, fontsize=11, fontweight='semibold', labelpad=10)
        line2 = ax2.plot(concurrency, avgs, marker='s', markersize=8, color=color, linewidth=2.5, linestyle='-.', label='Avg Latency (ms)')
        ax2.tick_params(axis='y', labelcolor=color)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')

        plt.title("System Concurrency Scaling: Throughput vs Average Latency", fontsize=13, fontweight='bold', pad=15)
        plt.tight_layout()
        scaling_file = os.path.join(RESULTS_DIR, "concurrency_scaling.png")
        plt.savefig(scaling_file, dpi=300)
        plt.close()
        print(f"Generated high-resolution chart: {scaling_file}")

    except Exception as e:
        print(f"Chart generation error: {e}")


def main():
    if not os.path.exists(SUMMARY_FILE):
        print(f"Error: {SUMMARY_FILE} not found.")
        sys.exit(1)

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    generate_publication_quality_charts(data)


if __name__ == "__main__":
    main()
