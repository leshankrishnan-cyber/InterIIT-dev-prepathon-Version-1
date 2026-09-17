import json
import os

from datetime import datetime

def create_incident(incident_id, scenario):
    directory = f"tester/results/{incident_id}"
    os.makedirs(directory, exist_ok=True)

    metadata = {
        "incident_id": incident_id,
        "scenario": scenario,
        "created_at": datetime.now().isoformat()
    }

    with open(f"{directory}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
