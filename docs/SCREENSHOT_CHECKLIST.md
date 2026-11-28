# Assignment 03 screenshots — Windows PowerShell

Run commands from the repository root in PowerShell. Keep the full terminal window
visible with its command and output; do not crop or annotate. Use your own cluster and
runs. Type each screenshot label (`A1`, `B1`, etc.) before its command.

All Kubernetes commands use context `ragops-dev` and namespace `ragops`.

## Start the port-forwards

Open two extra PowerShell windows and leave them running.

**Window 1 — candidate API**

```powershell
kubectl --context ragops-dev -n ragops port-forward service/candidate 18080:8000
```

**Window 2 — Ollama**

```powershell
kubectl --context ragops-dev -n ragops port-forward service/ollama 11434:11434
```

In the PowerShell window where you run Python commands, set the Ollama URL. Repeat
this whenever you open a new PowerShell window:

```powershell
$env:OLLAMA_URL = 'http://127.0.0.1:11434'
```

Check both connections before starting a long evaluation:

```powershell
Invoke-RestMethod http://127.0.0.1:18080/readyz
(Invoke-RestMethod http://127.0.0.1:11434/api/tags).models | Select-Object name
```

The Ollama list must include `nomic-embed-text`.

## A — Batch checks and unchanged ingestion

**A1 — Batch B verification report**

```powershell
Write-Output 'A1'
Get-Content eval/results/verification_report_20261123T200954Z-f924f005.md
```

For a newer Batch B run, show its report file from `eval/results` instead.

**A2 — second ingestion with the unchanged corpus**

```powershell
Write-Output 'A2'
kubectl --context ragops-dev -n ragops delete job ingest-unchanged --ignore-not-found
kubectl --context ragops-dev -n ragops create job ingest-unchanged --from=cronjob/ingest
kubectl --context ragops-dev -n ragops wait --for=condition=complete job/ingest-unchanged --timeout=40m
kubectl --context ragops-dev -n ragops logs job/ingest-unchanged
```

Show zero chunks embedded and the passing orphan check.

## B — all three evaluation levels

The candidate Service in this namespace currently serves a small fixture collection.
The full-corpus baseline and passing 420-word candidate were already evaluated in the
recorded run below. Use that complete measured comparison for B1; do not run the
29-question suite against the fixture Service.

**B1 — embedding/module, retrieval, and end-to-end summary from the full-corpus run**

```powershell
Write-Output 'B1'
Get-Content eval/results/comparison_candidate_420.md
```

This file contains the embedding/module, retrieval, and end-to-end metrics from the
team's full-corpus baseline and passing candidate runs.

## C — release gate

These are the recorded examples. For a new run, substitute its matching result paths.

**C1 — failing candidate**

```powershell
Write-Output 'C1'
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T203508248109Z_candidate.json --config config/gate.yaml
```

**C2 — passing candidate**

```powershell
Write-Output 'C2'
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T205940178644Z_candidate_420.json --config config/gate.yaml
```

Expected output: `REJECT` for C1 and `RELEASE` for C2.

## D — trace and prompt reconstruction

**D1 — full trace from a new query**

```powershell
Write-Output 'D1'
$trace = Invoke-RestMethod -Uri http://127.0.0.1:18080/query -Method Post -ContentType 'application/json' -Body '{"question":"How long can I borrow an audio recorder from the media desk?"}'
$trace | ConvertTo-Json -Depth 20
```

Copy the `trace_id`. For **D2**, replace `PASTE_TRACE_ID` with that value:

```powershell
Write-Output 'D2'
kubectl --context ragops-dev -n ragops exec deployment/api -- python -m ragops trace PASTE_TRACE_ID
```

Use the locker question in D1 when you want the trace to show the injected-content rail.

## E — coverage before and after expansion

Set `$env:OLLAMA_URL` as shown above in this same PowerShell window. After Python exits,
`$LASTEXITCODE` contains its real process exit code.

**E1 — original question set**

```powershell
Write-Output 'E1'
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden.jsonl --threshold 0.5409877865338792
$coverageExit = $LASTEXITCODE
Write-Output "exit code: $coverageExit"
```

**E2 — expanded question set**

```powershell
Write-Output 'E2'
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden_expanded.jsonl --threshold 0.5409877865338792
$coverageExit = $LASTEXITCODE
Write-Output "exit code: $coverageExit"
```

Recorded results were 65% / exit 1 before and 100% / exit 0 after. Call the expanded
result in-sample because the added questions were selected from uncovered live topics.

## F — Kubernetes evidence

**F1 — resources in the namespace**

```powershell
Write-Output 'F1'
kubectl --context ragops-dev -n ragops get all,pvc,configmap,cronjob,job
```

**F2 — completed ingestion Job**

```powershell
Write-Output 'F2'
kubectl --context ragops-dev -n ragops get jobs
kubectl --context ragops-dev -n ragops logs job/ingest
```

**F3 — completed evaluation Job**

```powershell
Write-Output 'F3'
kubectl --context ragops-dev -n ragops get jobs
kubectl --context ragops-dev -n ragops logs job/eval-optimized
```

If a Job has a different name, use the name shown by `get jobs`.

**F4 — gate outcomes after a ConfigMap-only edit**

Show the current ConfigMap and both recorded Kubernetes gate Jobs. The strict job failed;
the restored job passed. The same recorded candidate was used, without rebuilding the
image.

```powershell
Write-Output 'F4-before'
kubectl --context ragops-dev -n ragops get configmap gate-config -o yaml
kubectl --context ragops-dev -n ragops logs job/eval-fixture-strict
kubectl --context ragops-dev -n ragops logs job/eval-fixture-restored
```

**F5 — rollout, undo, and a new trace afterwards**

Open another PowerShell window and leave this API port-forward running:

```powershell
kubectl --context ragops-dev -n ragops port-forward service/api 18081:8000
```

In the screenshot window, perform the bad rollout and undo:

```powershell
Write-Output 'F5'
kubectl --context ragops-dev -n ragops rollout status deployment/api
kubectl --context ragops-dev -n ragops set env deployment/api CHROMA_COLLECTION=rahbar_kube_v1_nomic CHUNK_SIZE=400 TOP_K=1
kubectl --context ragops-dev -n ragops rollout status deployment/api
kubectl --context ragops-dev -n ragops rollout undo deployment/api
kubectl --context ragops-dev -n ragops rollout status deployment/api
```

Query the rolled-back API, copy its trace ID, then inspect that new trace. It should
show the restored collection and embedding version:

```powershell
$trace = Invoke-RestMethod -Uri http://127.0.0.1:18081/query -Method Post -ContentType 'application/json' -Body '{"question":"How long can I borrow an audio recorder from the media desk?"}'
$trace | Select-Object trace_id,collection,embedding_version
kubectl --context ragops-dev -n ragops exec deployment/api -- python -m ragops trace PASTE_NEW_TRACE_ID
```

## If a live API request disconnects

For a fresh query or evaluation (the recorded B1 summary above is a local file), check
the candidate and Ollama pods and recent logs:

```powershell
kubectl --context ragops-dev -n ragops get pods
kubectl --context ragops-dev -n ragops logs deployment/candidate --tail=80
kubectl --context ragops-dev -n ragops logs deployment/ollama --tail=80
```

If the candidate restarted, check its previous log:

```powershell
kubectl --context ragops-dev -n ragops logs deployment/candidate --previous --tail=80
```

## Before submitting

A team member must manually check at least eight synthetic questions against the source
pages. Update `reviewed`, `review_status`, and reviewer notes in both golden files, then
record the IDs in [GOLDEN_REVIEW.md](../eval/GOLDEN_REVIEW.md). Codex source checks do
not count as human review.
