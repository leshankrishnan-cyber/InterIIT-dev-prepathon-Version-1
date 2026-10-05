from .llm import analyze_with_llm
from .incident import load_incident
from .incident_analyzer import compare_incident

def investigate_incident(incident_id: str, description: str = "Automated investigation"):
    # 1. Detect state changes from the recorded timeline
    try:
        incident_data = load_incident(incident_id)
        timeline_changes = compare_incident(incident_data)
    except FileNotFoundError:
        timeline_changes = [{"change": "No local incident timeline data found."}]

    # 2. Pass the description and timeline to the LLM
    rca = analyze_with_llm(incident_id, description, timeline_changes)

    return {
        "incident_id": incident_id,
        "rca": rca
    }