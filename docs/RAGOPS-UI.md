# RAGOps chat UI

This UI runs inside the `ragops-dev` Minikube profile and calls the baseline RAGOps
API, which reads the full 724-chunk `rahbar_kube_full_nomic` collection. The existing
`rahbar` profile is a separate Assignment 02 deployment. The candidate Service remains
available for the Assignment 03 evaluation and release-gate workflow.

From the repository root in PowerShell, build and load the small UI image into the
RAGOps Minikube profile:

```powershell
docker build -t rahbar-ui:ragops ui
if ($LASTEXITCODE) { throw 'UI image build failed' }
minikube -p ragops-dev image load rahbar-ui:ragops
if ($LASTEXITCODE) { throw 'UI image load failed' }
```

Ensure the `ragops-dev` profile has the full-corpus collection and the expected model
pin, then apply the baseline API and UI manifests. Applying `api.yaml` points only the
baseline API at the full-corpus collection; it does not change the candidate used by
the evaluation gate.

```powershell
kubectl --context ragops-dev -n ragops apply -f k8s/api.yaml
kubectl --context ragops-dev -n ragops rollout status deployment/api --timeout=5m
kubectl --context ragops-dev -n ragops apply -f k8s/ragops-ui.yaml
kubectl --context ragops-dev -n ragops rollout status deployment/ragops-ui --timeout=3m
```

If the API does not become Ready, check that `rahbar_kube_full_nomic` exists in the
cluster Chroma service and that its embedding model matches the RAGOps ConfigMap. Do
not change the candidate collection to make the UI work.

Open the UI on port 18082. Port 18080 may already be occupied by an API port-forward.
Leave this command running in its terminal:

```powershell
kubectl --context ragops-dev -n ragops port-forward service/ragops-ui 18082:8080
```

Then visit [http://localhost:18082/?endpoint=/ragops/query](http://localhost:18082/?endpoint=/ragops/query).
The page sends same-origin requests through the UI's Nginx proxy to the RAGOps API,
so the browser does not need CORS access to a different port. Answers include citations,
retrieved passages, and the trace ID.
