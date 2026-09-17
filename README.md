# Kubernetes AI Agent for Root-Cause Analysis

Prototype for investigating Kubernetes incidents using Kubernetes state/events/logs, Prometheus metrics, Chaos Mesh, and an LLM reasoning layer.

(warning : you need your own openai api key for this version (to avoid me exhausting mine), will add one as a secret later)

## Stack

- Kubernetes: kind

- Backend: FastAPI

- Database: PostgreSQL

- Frontend: plain HTML/CSS/JavaScript

- Metrics: kube-prometheus-stack / Prometheus

- Failure injection: Chaos Mesh

- LLM: OpenAI API (will change to something free later)

- Incident evidence: BEFORE / DURING / AFTER

## Project structure

```
k8s-rca/
├── app/
│   ├── api/
│   │   ├── agent/
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── database/init.sql
│   └── frontend/
├── kubernetes/
├── chaos/
├── tester/
├── docker-compose.yml
└── README.md
```

## Requirements

Install:

```
docker --version
kind --version
kubectl version --client
helm version
python3 --version
```

Python 3.12+ is recommended.


# These Commands are to be run from k8s-rca/

# 1. Create the kind cluster

```
kind create cluster \
 --name rca-cluster \
 --config kubernetes/kind-config.yaml
```

Check:

```
kubectl get nodes
```

you should see 1 control-plane and 2 normal nodes labeleed \<none\>.


# 2. Install Prometheus

```
helm repo add prometheus-community \
 https://prometheus-community.github.io/helm-charts

helm repo update

kubectl create namespace monitoring

#WARNING WARNING ATTENTION PLSSS DO NOT COPY the entire thing at once bcs else the installation will timeout , and it does take a bit so pls wait patiently and enter each command one at a time (or u can do the above half then the below half that works too)

helm install prometheus \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring
```

Check:

```
kubectl get pods -n monitoring

#sould get these terms
alert manager , prometheus , kube
```

Access Prometheus:

```
kubectl port-forward \
  -n monitoring \
  svc/prometheus-kube-prometheus-prometheus \
  9090:9090
```

Open:

```
http://localhost:9090
```


# 3. Install Chaos Mesh

```
helm repo add chaos-mesh \
  https://charts.chaos-mesh.org

helm repo update

kubectl create namespace chaos-mesh

helm install chaos-mesh \
  chaos-mesh/chaos-mesh \
  --namespace chaos-mesh \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock
```

Check:

```
kubectl get pods -n chaos-mesh

will see terms like chaos , controler,manager, daemon
```



# 4. Build the application

```
docker build -t rca-api:latest ./app/api
docker build -t rca-frontend:latest ./app/frontend
```

Load images into kind:

```
kind load docker-image rca-api:latest --name rca-cluster
kind load docker-image rca-frontend:latest --name rca-cluster
```


# 5. Deploy PostgreSQL, API and frontend

```
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/api.yaml
kubectl apply -f kubernetes/frontend.yaml
kubectl apply -f kubernetes/api-servicemonitor.yaml
```

Check:

```
kubectl get all -n rca
```

Wait for the Pods:

```
kubectl get pods -n rca -w
```


# 6. Start the application

Frontend:

```
kubectl port-forward \
  -n rca \
  svc/frontend-service \
  3000:80
```

Open:

```
http://localhost:3000
```

API, in another terminal:

```
kubectl port-forward \
  -n rca \
  svc/api-service \
  8000:8000
```

Test:

```
curl http://localhost:8000/health
```

Metrics:

```
curl http://localhost:8000/metrics
```

Constants:

```
curl http://localhost:8000/constants
```


# 7. Set up the tester

From the project root:

```
pip install requests
```

The tester writes incidents to:

```
tester/results/
```

Each incident has:

```
INC-YYYYMMDD-HHMMSS/
├── metadata.json
├── before/
├── during/
└── after/
```


# 8. Generate an incident

Make sure the Prometheus port-forward is running on port 9090.

Run:

```
python tester/runner.py pod_kill
```

Other currently registered automated scenarios:

```
python tester/runner.py cpu_stress
python tester/runner.py memory_stress
python tester/runner.py network_delay
python tester/runner.py network_loss
python tester/runner.py application_crash
python tester/runner.py database_crash
python tester/runner.py node_failure
python tester/runner.py dns_failure
```

The tester performs:

```
BEFORE
  ↓
inject failure
  ↓
wait
  ↓
DURING
  ↓
remove/recover
  ↓
wait
  ↓
AFTER
```

Evidence includes Kubernetes state, events, node state, logs, and Prometheus queries.


# 9. Inspect an incident

List incidents:

```
find tester/results \
  -maxdepth 1 \
  -mindepth 1 \
  -type d
```

Inspect one:

```
find tester/results/INC-... -type f
```


# 10. Configure the LLM

Set the OpenAI API key in the environment used by the API:

```
export OPENAI_API_KEY="your-api-key"
```

For local API development:

```
cd app/api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export OPENAI_API_KEY="your-api-key"

uvicorn main:app --reload --port 8000
```

The current LLM layer expects the OpenAI Python SDK and uses the Responses API.


# 11. Incident-aware RCA

The RCA endpoint accepts an incident ID:

```
GET /investigate/{incident_id}
```

For example:

```
curl \
  http://localhost:8000/investigate/INC-20260917-214500
```

The agent loads:

```
incident
├── metadata
├── before
├── during
└── after
```

It then performs change detection and sends the incident timeline to the LLM.

Expected RCA structure:

```
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
```


# 12. Full first test

Terminal 1:

```
kubectl port-forward \
  -n monitoring \
  svc/prometheus-kube-prometheus-prometheus \
  9090:9090
```

Terminal 2:

```
kubectl port-forward \
  -n rca \
  svc/api-service \
  8000:8000
```

Terminal 3:

```
python tester/runner.py pod_kill
```

Find the incident ID:

```
find tester/results \
  -maxdepth 1 \
  -mindepth 1 \
  -type d
```

Then:

```
curl http://localhost:8000/investigate/INC-XXXXXXXX-XXXXXX
```


# 13. Docker Compose

The original application can also be started without Kubernetes:

```
docker compose up --build
```

Services:

```
frontend → localhost:3000
api      → localhost:8000
postgres → localhost:5432
```

Stop:

```
docker compose down
```

For the RCA/Kubernetes prototype, the kind setup is the primary environment.


# Current scope

Implemented:

- FastAPI application

- PostgreSQL constants database

- Docker/Compose setup

- 3-node kind cluster

- Kubernetes application deployment

- Prometheus monitoring

- FastAPI metrics

- ServiceMonitor

- Chaos Mesh

- Pod kill

- CPU stress

- Memory stress

- Network delay

- Packet loss

- Application crash

- Database Pod kill

- Node failure

- Container/configuration experiment manifests

- Automated incident recorder

- BEFORE/DURING/AFTER evidence

- Prometheus evidence collection

- Deterministic Kubernetes analysis

- Incident-aware LLM RCA pipeline

Not yet implemented:

- Evidence citations attached to individual RCA claims

- Complete HTTPChaos suite

- Complete storage failure suite

- Complete probe failure suite

- Complete database degradation suite

- Compound-incident automation

- Final RCA dashboard

- Production secret/authentication setup

