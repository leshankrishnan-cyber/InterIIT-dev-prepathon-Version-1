import json
import os
import subprocess
import sys
import time
from datetime import datetime

RESULTS_DIR = "tester/results"

def run(command):
    print(f"$ {command}")

    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode

def collect(incident_id, phase):
    print(f"\n===== COLLECTING {phase.upper()} =====")
    run(f"python tester/collect.py {incident_id} {phase}")
    run(f"python tester/prometheus.py {incident_id} {phase}")

def create_metadata(incident_id, scenario):
    directory = f"{RESULTS_DIR}/{incident_id}"
    os.makedirs(directory, exist_ok=True)

    metadata = {
        "incident_id": incident_id,
        "scenario": scenario,
        "created_at": datetime.now().isoformat()
    }

    with open(f"{directory}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

def run_chaos(manifest):
    run(f"kubectl apply -f {manifest}")
    print("\n===== FAILURE ACTIVE =====")
    time.sleep(30)

def run_http_failure(url):
    run(f"curl -s {url}")
    print("\n===== APPLICATION FAILURE TRIGGERED =====")
    time.sleep(30)

def run_node_failure(node):
    run(f"docker stop {node}")
    print("\n===== NODE FAILURE ACTIVE =====")
    time.sleep(30)

def main():
    if len(sys.argv) != 2:
        print("Usage: python tester/runner.py <scenario>")
        sys.exit(1)

    scenario_name = sys.argv[1]

    with open("tester/scenarios/scenarios.json") as f:
        scenarios = json.load(f)

    if scenario_name not in scenarios:
        print(f"Unknown scenario: {scenario_name}")
        print("Available scenarios:")
        for name in scenarios:
            print(f"  {name}")
        sys.exit(1)

    scenario = scenarios[scenario_name]

    if scenario["type"] == "manual":
        print("This scenario is currently manual.")
        print(f"kubectl apply -f {scenario['manifest']}")
        return

    incident_id = "INC-" + datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"\nIncident: {incident_id}")
    print(f"Scenario: {scenario_name}")

    create_metadata(incident_id, scenario_name)

    collect(incident_id, "before")

    print("\n===== INJECTING FAILURE =====")

    if scenario["type"] == "chaos":
        run_chaos(scenario["manifest"])
    elif scenario["type"] == "http":
        run_http_failure(scenario["url"])
    elif scenario["type"] == "node":
        run_node_failure(scenario["node"])

    collect(incident_id, "during")

    if scenario["type"] == "chaos":
        run(f"kubectl delete -f {scenario['manifest']}")
    elif scenario["type"] == "node":
        run(f"docker start {scenario['node']}")

    print("\n===== WAITING FOR RECOVERY =====")
    time.sleep(30)

    collect(incident_id, "after")

    print("\n================================")
    print("INCIDENT COMPLETE")
    print(f"ID: {incident_id}")
    print(f"Results: {RESULTS_DIR}/{incident_id}")
    print("================================")

if __name__ == "__main__":
    main()
