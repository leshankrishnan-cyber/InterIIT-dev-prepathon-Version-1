from .llm import analyze_with_llm

def investigate_incident(incident_id):
    # The agent now dynamically investigates the live environment via tools!
    rca = analyze_with_llm(incident_id)

    return {
        "incident_id": incident_id,
        "rca": rca
    }