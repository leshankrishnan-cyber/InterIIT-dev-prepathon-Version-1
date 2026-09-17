from .incident import load_incident
from .incident_analyzer import compare_incident
from .llm import analyze_with_llm

def investigate_incident(incident_id):
    incident = load_incident(incident_id)
    changes = compare_incident(incident)
    rca = analyze_with_llm(incident, changes)

    return {
        "incident_id": incident_id,
        "changes": changes,
        "rca": rca
    }
