import subprocess

def run(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def collect_kubernetes_evidence():
    return {
        "pods": run("kubectl get pods -n rca -o wide"),
        "deployments": run("kubectl get deployments -n rca -o wide"),
        "services": run("kubectl get services -n rca"),
        "events": run("kubectl get events -n rca --sort-by=.lastTimestamp"),
        "nodes": run("kubectl get nodes -o wide"),
        "pod_descriptions": run("kubectl describe pods -n rca")
    }
