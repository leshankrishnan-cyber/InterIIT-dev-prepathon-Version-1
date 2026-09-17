def compare_incident(incident):
    before = incident["before"]
    during = incident["during"]
    after = incident["after"]

    changes = []

    if before.get("pods.txt", "") != during.get("pods.txt", ""):
        changes.append({
            "component": "pods",
            "change": "Pod state changed during the incident"
        })

    if during.get("pods.txt", "") != after.get("pods.txt", ""):
        changes.append({
            "component": "pods",
            "change": "Pod state changed during recovery"
        })

    if before.get("events.txt", "") != during.get("events.txt", ""):
        changes.append({
            "component": "events",
            "change": "Kubernetes events changed during incident"
        })

    if before.get("nodes.txt", "") != during.get("nodes.txt", ""):
        changes.append({
            "component": "nodes",
            "change": "Node state changed during incident"
        })

    return changes
