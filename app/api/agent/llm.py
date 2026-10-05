import json
import os
from google import genai
from google.genai import types

from .collector import get_pods, get_pod_logs, get_events, get_deployments
from .metrics import query as query_prom

# Initialize the Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def query_prometheus(metric_query: str) -> str:
    """Queries Prometheus for metrics. Use valid PromQL."""
    try:
        result = query_prom(metric_query)
        # Truncate string response to prevent exceeding context window
        return str(result)[:2000]
    except Exception as e:
        return f"Error: {e}"

# Register the Python functions as AI Tools
TOOLS = [get_pods, get_pod_logs, get_events, get_deployments, query_prometheus]

SYSTEM_PROMPT = """You are an autonomous Kubernetes root-cause analysis agent.
Investigate the cluster dynamically using your tools.
1. Start by checking pods and events in the 'rca' namespace.
2. If pods are failing, fetch their logs.
3. Query metrics to check for resource exhaustion (OOM/CPU) or network/database failures.
4. Reason about competing hypotheses.

When you have enough evidence to reach a conclusion, return a final JSON block matching this structure exactly (and output nothing else):
{
  "summary": "...",
  "symptoms": ["..."],
  "hypotheses": [
    {
      "cause": "...",
      "supporting_evidence": ["..."],
      "contradicting_evidence": ["..."]
    }
  ],
  "likely_root_cause": "...",
  "confidence": "High/Medium/Low",
  "recommended_checks": ["..."]
}
"""

def analyze_with_llm(incident_id: str, description: str):
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,
        tools=TOOLS
    )
    
    # The chats interface automatically handles the iterative tool-calling loop
    chat = client.chats.create(model="gemini-3.8-flash", config=config)
    prompt = (
        f"Incident Alert: {description}\n"
        f"Incident ID: {incident_id}\n"
        "Investigate the cluster dynamically using your tools to determine the root cause, "
        "and return your findings in the required JSON format."
    )
    
    try:
        response = chat.send_message(prompt)
        text = response.text.strip()
        
        # Clean up markdown formatting if present
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        return {
            "summary": f"Agent failed to complete investigation: {str(e)}",
            "likely_root_cause": "Unknown",
            "confidence": "None"
        }