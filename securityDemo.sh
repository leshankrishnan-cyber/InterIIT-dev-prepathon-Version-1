#!/bin/bash
echo "=== RCA Agent Security Sandbox Demonstration ==="

echo -e "\n1. Can the agent read pods? (Expected: yes)"
kubectl auth can-i get pods --as=system:serviceaccount:rca:rca-agent-sa -n rca

echo -e "\n2. Can the agent delete pods? (Expected: no - prevents destructive action)"
kubectl auth can-i delete pods --as=system:serviceaccount:rca:rca-agent-sa -n rca

echo -e "\n3. Can the agent read secrets? (Expected: no - prevents credential theft)"
kubectl auth can-i get secrets --as=system:serviceaccount:rca:rca-agent-sa -n rca

echo -e "\n4. Can the agent execute arbitrary commands in a pod? (Expected: no)"
kubectl auth can-i create pods/exec --as=system:serviceaccount:rca:rca-agent-sa -n rca