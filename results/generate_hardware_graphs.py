import matplotlib.pyplot as plt
import os

results_dir = r"C:\uni\sem5\cclab\movie-concert-microservices\results"

# Data we collected from docker stats
concurrency = [1, 2, 4, 8, 16]
cpu = [25.31, 74.60, 133.31, 147.50, 149.34]
memory = [26.45, 26.65, 27.67, 27.97, 28.33]

# 1. CPU Graph
plt.figure(figsize=(8, 5))
plt.plot(concurrency, cpu, marker='o', color='#ef4444', linewidth=2, markersize=8)
plt.title("Concurrent Requests vs CPU Utilization (API Gateway)")
plt.xlabel("Concurrent Requests")
plt.ylabel("Peak CPU Utilization (%)")
plt.xticks(concurrency)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(results_dir, "cpu_utilization.png"), dpi=300)
plt.close()

# 2. Memory Graph
plt.figure(figsize=(8, 5))
plt.plot(concurrency, memory, marker='s', color='#3b82f6', linewidth=2, markersize=8)
plt.title("Concurrent Requests vs Memory Utilization (API Gateway)")
plt.xlabel("Concurrent Requests")
plt.ylabel("Peak Memory Utilization (MiB)")
plt.xticks(concurrency)
plt.ylim(0, 50) # Set Y limit to 50 to show it's mostly flat
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(results_dir, "memory_utilization.png"), dpi=300)
plt.close()

print("Hardware graphs generated successfully!")
