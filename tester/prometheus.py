import json
import os
import sys
import requests

PROMETHEUS_URL = "http://localhost:9090"

QUERIES = {
    "pod_restarts":
        'kube_pod_container_status_restarts_total{namespace="rca"}',
    "pod_phase":
        'kube_pod_status_phase{namespace="rca"}',
    "cpu":
        'rate(container_cpu_usage_seconds_total{namespace="rca"}[1m])',
    "memory":
        'container_memory_working_set_bytes{namespace="rca"}',
    "http_requests":
        'http_requests_total',
    "http_latency":
        'http_request_duration_seconds'
}

def query_prometheus(query):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10
    )
    return response.json()

def collect(incident_id, phase):
    directory = f"tester/results/{incident_id}/{phase}"
    os.makedirs(directory, exist_ok=True)

    for name, query in QUERIES.items():
        try:
            result = query_prometheus(query)
        except Exception as exc:
            result = {"error": str(exc)}

        with open(
            f"{directory}/prometheus-{name}.json",
            "w"
        ) as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python prometheus.py <incident_id> <phase>")
        sys.exit(1)

    collect(sys.argv[1], sys.argv[2])
