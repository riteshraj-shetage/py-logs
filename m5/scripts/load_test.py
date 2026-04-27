#!/usr/bin/env python3
"""
Standalone load-testing script using only stdlib (threading + urllib.request).

Usage:
    python scripts/load_test.py [--url URL] [--concurrency N] [--requests N]
"""
import argparse
import statistics
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict


def make_request(url: str, results: list, index: int):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except Exception:
        status = 0
    elapsed_ms = (time.perf_counter() - start) * 1000
    results[index] = (status, elapsed_ms)


def run_load_test(url: str, concurrency: int, total: int):
    print(f"\n{'='*55}")
    print(f"  Load Test")
    print(f"  URL         : {url}")
    print(f"  Concurrency : {concurrency}")
    print(f"  Total reqs  : {total}")
    print(f"{'='*55}\n")

    results = [None] * total
    batches = [results[i : i + concurrency] for i in range(0, total, concurrency)]

    overall_start = time.perf_counter()
    completed = 0
    for batch_results in [results[i : i + concurrency] for i in range(0, total, concurrency)]:
        batch_index_start = completed
        threads = []
        for j in range(len(batch_results)):
            t = threading.Thread(target=make_request, args=(url, results, batch_index_start + j))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        completed += len(batch_results)

    total_time = time.perf_counter() - overall_start

    latencies = [r[1] for r in results if r is not None]
    status_counts = defaultdict(int)
    for r in results:
        if r:
            status_counts[r[0]] += 1

    if latencies:
        latencies_sorted = sorted(latencies)
        p50 = statistics.median(latencies_sorted)
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]
        rps = len(latencies) / total_time

        print(f"  Results")
        print(f"  -------")
        print(f"  Total time      : {total_time:.2f}s")
        print(f"  Completed reqs  : {len(latencies)}")
        print(f"  Req/sec         : {rps:.1f}")
        print(f"  Latency min     : {min(latencies):.1f} ms")
        print(f"  Latency avg     : {statistics.mean(latencies):.1f} ms")
        print(f"  Latency p50     : {p50:.1f} ms")
        print(f"  Latency p95     : {p95:.1f} ms")
        print(f"  Latency p99     : {p99:.1f} ms")
        print(f"  Latency max     : {max(latencies):.1f} ms")
        print(f"\n  Status codes    : {dict(status_counts)}")
    print(f"{'='*55}\n")


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP load tester")
    parser.add_argument("--url", default="http://localhost:8000/products", help="Target URL")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent threads per batch")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests")
    args = parser.parse_args()
    run_load_test(args.url, args.concurrency, args.requests)


if __name__ == "__main__":
    main()
