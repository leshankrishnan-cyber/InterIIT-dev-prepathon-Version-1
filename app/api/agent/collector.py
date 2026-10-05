from kubernetes import client, config

# Load cluster config. When running in-cluster, it uses the service account.
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

def get_pods(namespace: str = "rca") -> str:
    """Returns a list of pods and their current status in the given namespace."""
    try:
        pods = v1.list_namespaced_pod(namespace)
        results = [f"Pod: {p.metadata.name}, Status: {p.status.phase}" for p in pods.items]
        return "\n".join(results) if results else "No pods found."
    except Exception as e:
        return f"Error fetching pods: {str(e)}"

def get_pod_logs(pod_name: str, namespace: str = "rca") -> str:
    """Fetches the recent logs for a specific pod."""
    try:
        # Limit logs to avoid context window explosion
        logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=50)
        return logs
    except Exception as e:
        return f"Error fetching logs for {pod_name}: {str(e)}"

def get_events(namespace: str = "rca") -> str:
    """Fetches recent Kubernetes events (like crashes, scheduling failures, OOM kills)."""
    try:
        events = v1.list_namespaced_event(namespace)
        # Sort by timestamp and get the latest 20
        sorted_events = sorted(events.items, key=lambda x: x.last_timestamp or x.event_time, reverse=True)[:20]
        results = [f"{e.type} - {e.reason}: {e.message} (Pod: {e.involved_object.name})" for e in sorted_events]
        return "\n".join(results) if results else "No recent events."
    except Exception as e:
        return f"Error fetching events: {str(e)}"

def get_deployments(namespace: str = "rca") -> str:
    """Returns the state of deployments and their replicas."""
    try:
        deps = apps_v1.list_namespaced_deployment(namespace)
        results = [f"Deployment: {d.metadata.name}, Replicas: {d.status.ready_replicas}/{d.status.replicas}" for d in deps.items]
        return "\n".join(results) if results else "No deployments found."
    except Exception as e:
        return f"Error fetching deployments: {str(e)}"