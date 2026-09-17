import json
import os

RESULTS_DIR = "/app/incident-results"

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def load_phase(incident_dir, phase):
    phase_dir = os.path.join(incident_dir, phase)

    if not os.path.isdir(phase_dir):
        return {}

    evidence = {}

    for filename in os.listdir(phase_dir):
        path = os.path.join(phase_dir, filename)

        if not os.path.isfile(path):
            continue

        if filename.endswith(".json"):
            try:
                with open(path, "r") as f:
                    evidence[filename] = json.load(f)
            except Exception:
                evidence[filename] = read_file(path)
        else:
            evidence[filename] = read_file(path)

    return evidence

def load_incident(incident_id):
    incident_dir = os.path.join(RESULTS_DIR, incident_id)

    if not os.path.isdir(incident_dir):
        raise FileNotFoundError(
            f"Incident {incident_id} not found"
        )

    metadata = {}
    metadata_path = os.path.join(incident_dir, "metadata.json")

    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    return {
        "metadata": metadata,
        "before": load_phase(incident_dir, "before"),
        "during": load_phase(incident_dir, "during"),
        "after": load_phase(incident_dir, "after")
    }
