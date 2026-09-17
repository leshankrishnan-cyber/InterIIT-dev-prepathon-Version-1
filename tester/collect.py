import os
import subprocess
import sys

def run(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def collect(incident_id, phase):
    directory = f"tester/results/{incident_id}/{phase}"
    os.makedirs(directory, exist_ok=True)

    commands = {
        "pods": "kubectl get pods -n rca -o wide",
        "deployments": "kubectl get deployments -n rca -o wide",
        "services": "kubectl get services -n rca",
        "events": "kubectl get events -n rca --sort-by=.lastTimestamp",
        "nodes": "kubectl get nodes -o wide",
        "chaos": "kubectl get podchaos,networkchaos,stresschaos -A",
    }

    for name, command in commands.items():
        with open(f"{directory}/{name}.txt", "w") as f:
            f.write(run(command))

    pods = run(
        "kubectl get pods -n rca "
        "-o jsonpath='{range .items[*]}{.metadata.name}{\"\\n\"}{end}'"
    )

    for pod in pods.strip().splitlines():
        pod = pod.strip("'")
        if not pod:
            continue

        logs = run(
            f"kubectl logs {pod} -n rca --all-containers=true"
        )

        with open(f"{directory}/logs-{pod}.txt", "w") as f:
            f.write(logs)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python collect.py <incident_id> <phase>")
        sys.exit(1)

    collect(sys.argv[1], sys.argv[2])
