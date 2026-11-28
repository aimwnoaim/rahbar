# Assignment 03 screenshots

Take each screenshot in a full terminal window. Keep the command and its output
visible; do not crop or annotate. Type the item label (`A1`, `B1`, etc.) before each
command. Use your own Minikube cluster and runs. Run these from the repo root in Bash.

The commands below use the Assignment 03 context `ragops-dev` and namespace `ragops`.
In the terminal, run this once to make the Kubernetes commands shorter:

```bash
alias k='kubectl --context ragops-dev -n ragops'
```

For B and D, open a second terminal and leave this running:

```bash
kubectl --context ragops-dev -n ragops port-forward service/candidate 18080:8000
```

## A — Batch checks and unchanged ingestion

**A1 — Batch B verification report**

```bash
echo A1
cat eval/results/verification_report_20261123T200954Z-f924f005.md
```

This report is from the recorded Batch B run. For a newer run, use its report filename
from `eval/results/`.

**A2 — second ingestion, unchanged corpus**

```bash
echo A2
k delete job ingest-unchanged --ignore-not-found
k create job ingest-unchanged --from=cronjob/ingest
k wait --for=condition=complete job/ingest-unchanged --timeout=40m
k logs job/ingest-unchanged
```

Show that it embedded zero chunks and passed the orphan check.

## B — evaluation summary

**B1 — embedding/module, retrieval, and end-to-end results**

```bash
echo B1
python -m ragops eval --collection rahbar_v3_nomic --target-url http://localhost:18080 --out eval/results --label appendix
```

The command prints the result file path. Open its matching `.md` summary in the terminal
if needed so all three evaluation levels are visible.

## C — release gate

Use the baseline and candidate results from your own runs. These are the recorded
examples; replace the paths if you make new runs.

**C1 — failing candidate**

```bash
echo C1
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T203508248109Z_candidate.json --config config/gate.yaml
```

**C2 — passing candidate**

```bash
echo C2
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T205940178644Z_candidate_420.json --config config/gate.yaml
```

The output should say `REJECT` for C1 and `RELEASE` for C2.

## D — trace and prompt reconstruction

For **D1**, send a query to the candidate service. The response includes the complete
trace. Use the planted locker instruction question if you need to show the guardrail.

```bash
echo D1
curl -fsS -X POST http://localhost:18080/query -H 'Content-Type: application/json' -d '{"question":"How long can I borrow an audio recorder from the media desk?"}'
```

Copy the `trace_id` from that output. For **D2**, replace `PASTE_TRACE_ID` below:

```bash
echo D2
k exec deploy/api -- python -m ragops trace PASTE_TRACE_ID
```

## E — coverage before and after adding questions

**E1 — original question set**

```bash
echo E1
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden.jsonl --threshold 0.5409877865338792
echo "exit code: $?"
```

**E2 — expanded question set**

```bash
echo E2
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden_expanded.jsonl --threshold 0.5409877865338792
echo "exit code: $?"
```

Expected recorded results are 65% / exit 1 before, and 100% / exit 0 after. Mention
that the expanded result is in-sample because those questions were chosen from uncovered
live topics.

## F — Kubernetes deployment and rollback

**F1 — namespace resources**

```bash
echo F1
k get all,pvc,configmap,cronjob,job
```

**F2 — completed ingestion Job**

```bash
echo F2
k get jobs
k logs job/ingest
```

**F3 — completed evaluation Job**

```bash
echo F3
k get jobs
k logs job/eval
```

If your Jobs have different names, use the names shown by `k get jobs`.

**F4 — gate changes after editing the ConfigMap**

First show the current setting, then edit it:

```bash
echo F4-before
k get configmap gate-config -o yaml
k edit configmap gate-config
```

Set `p95_latency_baseline_factor` to `0`, save, then run these commands. The gate Job
should fail. No image rebuild is needed.

```bash
k delete job eval --ignore-not-found
k apply -f k8s/eval-job.yaml
k wait --for=condition=failed job/eval --timeout=40m
k logs job/eval
```

Restore the original ConfigMap and rerun the Job to show the passing result:

```bash
k apply -f k8s/config.yaml
k delete job eval --ignore-not-found
k apply -f k8s/eval-job.yaml
k wait --for=condition=complete job/eval --timeout=40m
k logs job/eval
```

**F5 — rollout, undo, and a new trace after undo**

```bash
echo F5-rollout
k rollout status deployment/api
k set env deployment/api CHROMA_COLLECTION=rahbar_kube_v1_nomic CHUNK_SIZE=400 TOP_K=1
k rollout status deployment/api
k rollout undo deployment/api
k rollout status deployment/api
```

Send a fresh question to the API and copy the new `trace_id` from its output:

```bash
curl -fsS -X POST http://localhost:18080/query -H 'Content-Type: application/json' -d '{"question":"How long can I borrow an audio recorder from the media desk?"}'
```

Then show its trace. It must show the restored collection and embedding version:

```bash
k exec deploy/api -- python -m ragops trace PASTE_NEW_TRACE_ID
```

## Before submitting

Have a team member manually check at least eight synthetic questions against their
source pages. Update `reviewed`, `review_status`, and reviewer notes in both golden
files. Record the IDs in [GOLDEN_REVIEW.md](../eval/GOLDEN_REVIEW.md). Do not label
Codex's source checks as human review.
