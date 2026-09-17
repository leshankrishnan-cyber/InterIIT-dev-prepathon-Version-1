import requests

PROMETHEUS_URL = (
    "http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090"
)

def query(query):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10
    )
    return response.json()

def collect_metrics():
    return {
        "pod_restarts": query(
            'kube_pod_container_status_restarts_total{namespace="rca"}'
        ),
        "pod_phase": query(
            'kube_pod_status_phase{namespace="rca"}'
        ),
        "cpu": query(
            'rate(container_cpu_usage_seconds_total{namespace="rca"}[5m])'
        ),
        "memory": query(
            'container_memory_working_set_bytes{namespace="rca"}'
        ),
        "http_requests": query('http_requests_total'),
        "http_latency": query('http_request_duration_seconds')
    }
