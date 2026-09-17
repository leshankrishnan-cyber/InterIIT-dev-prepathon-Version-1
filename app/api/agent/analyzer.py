def analyze(evidence):
    findings = []

    pods = evidence.get("pods", "")
    events = evidence.get("events", "")
    nodes = evidence.get("nodes", "")

    if "CrashLoopBackOff" in pods:
        findings.append("A Pod is repeatedly crashing.")

    if "OOMKilled" in pods:
        findings.append(
            "A container was killed because of memory exhaustion."
        )

    if "ImagePullBackOff" in pods:
        findings.append(
            "A container image could not be pulled."
        )

    if "ErrImagePull" in pods:
        findings.append(
            "Kubernetes failed to pull a container image."
        )

    if "FailedScheduling" in events:
        findings.append(
            "Kubernetes was unable to schedule a Pod."
        )

    if "NotReady" in nodes:
        findings.append(
            "A Kubernetes node is not Ready."
        )

    if not findings:
        findings.append(
            "No obvious Kubernetes failure signature was detected."
        )

    return findings
