import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a Kubernetes root-cause analysis agent.

Analyze the supplied Kubernetes and Prometheus evidence.

Your task is to:
1. Identify observed symptoms.
2. Generate plausible hypotheses.
3. Compare each hypothesis against the evidence.
4. Identify the most likely root cause.
5. Distinguish root causes from downstream symptoms.
6. State uncertainty when evidence is insufficient.

Do not invent evidence.

Return JSON with this structure:

{
  "summary": "...",
  "symptoms": [],
  "hypotheses": [
    {
      "cause": "...",
      "supporting_evidence": [],
      "contradicting_evidence": []
    }
  ],
  "likely_root_cause": "...",
  "confidence": "...",
  "recommended_checks": []
}
"""

def analyze_with_llm(incident, changes):
    prompt = {
        "incident": incident,
        "detected_changes": changes
    }

    response = client.responses.create(
        model="gpt-5.6",
        instructions=SYSTEM_PROMPT,
        input=json.dumps(prompt, indent=2, default=str)
    )

    text = response.output_text

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "summary": text,
            "symptoms": [],
            "hypotheses": [],
            "likely_root_cause": "Unable to parse structured response",
            "confidence": "unknown",
            "recommended_checks": []
        }
