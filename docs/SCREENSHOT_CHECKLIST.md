# Assignment 03 screenshot appendix

Capture each item from a terminal on the submitting team's own Minikube cluster and
own run. Keep the full terminal window visible, including the command and all output;
do not crop, annotate, or substitute a stored result for a required live-cluster
screenshot. Use one terminal window per screenshot when output is long. Type the item
label (for example `B3`) as a visible command immediately before the evidence.

These commands use Bash from the repository root. They target only Minikube profile
and kubectl context `ragops-dev`, namespace `ragops`; do not mix them with the separate
Assignment 02 `rahbar` profile. Start the RAGOps environment using [k8s/README.md](../k8s/README.md).

```bash
k=(kubectl --context ragops-dev -n ragops)
```

## A — verification and incremental indexing

**A1 — Batch B checks and quarantine reasons.** Use the verification report from the
Batch B run performed on your cluster. The report lists each check's pass/fail result,
the outcome, and the reason for quarantine.

```bash
echo A1
cat eval/results/verification_report_20261123T200954Z-f924f005.md
```

For a newly captured run, replace that filename with the run ID printed by the ingest
Job. Do not present the committed historical report as a new run.

**A2 — unchanged second ingestion.** After the Batch A corpus is loaded and the first
ingestion Job completes, run the same Job template again without changing `/data/inbox`.
Keep the second run's Job name unique:

```bash
echo A2
job="ingest-unchanged-$(date +%Y%m%d%H%M%S)"
"${k[@]}" create job "$job" --from=cronjob/ingest
"${k[@]}" wait --for=condition=complete "job/$job" --timeout=40m
"${k[@]}" logs "job/$job"
```

The output must show `chunks_embedded: 0` and a passing orphan check. If the CronJob
does not exist yet, apply `k8s/ingest-cronjob.yaml` after completing the setup steps.

## B — three-level evaluation

**B1 — evaluation summary.** Run against your current candidate Service and show the
module/embedding, retrieval, and end-to-end sections in the timestamped summary.

```bash
echo B1
python -m ragops eval --collection rahbar_v3_nomic --target-url http://localhost:18080 --out eval/results --label appendix
```

Before running, start `kubectl --context ragops-dev -n ragops port-forward service/candidate 18080:8000`
in another terminal. Use the generated JSON/Markdown path printed by the command and
display its summary in the same terminal if it does not fit in the current viewport.

## C — regression gate

The checked-in evidence uses a 600-word candidate that fails and a 420-word candidate
that passes. For screenshot-grade evidence, run these commands against the matching
baseline/candidate result files produced by your current cluster. Confirm both files
are in the same split and are from the same evaluator version.

```bash
echo C1
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T203508248109Z_candidate.json --config config/gate.yaml; test "$?" -eq 1
```

```bash
echo C2
python -m ragops gate --baseline eval/results/eval_20261123T200917344381Z_batch_a.json --candidate eval/results/eval_20261123T205940178644Z_candidate_420.json --config config/gate.yaml
```

The commands above replay recorded results. For the assignment's own-cluster screenshot,
use the corresponding current-run result paths instead; the terminal must show `REJECT`
for C1 and `RELEASE` for C2.

## D — trace and prompt reconstruction

**D1 — one complete trace from a fresh query.** Start the API port-forward in another
terminal and query it; this prints the full trace record, including guardrail actions,
collection, model version, and prompt hash.

```bash
echo D1
curl -fsS -X POST http://127.0.0.1:18080/query -H 'Content-Type: application/json' -d '{"question":"How long can I borrow an audio recorder from the media desk?"}' | tee /tmp/ragops-trace.json
```

**D2 — trace tool rebuilding the prompt.** Use the `trace_id` printed by the D1 query.

```bash
echo D2
trace_id=$(python -c 'import json; print(json.load(open("/tmp/ragops-trace.json"))["trace_id"])')
"${k[@]}" exec deploy/api -- python -m ragops trace "$trace_id"
```

For the planted Batch B instruction, query the locker question and show the trace's
`guardrail_actions` entry with `action: drop` before taking the D2 screenshot.

## E — live-question coverage

Capture coverage before and after adding the new questions using the calibrated value
and the two committed golden files. The initial set should fail the threshold; the
expanded set should pass. Preserve the exit code visibly.

```bash
echo E1-before
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden.jsonl --threshold 0.5409877865338792; echo "exit=$?"
```

```bash
echo E2-after
python -m ragops coverage --live eval/live_queries.jsonl --golden eval/golden_expanded.jsonl --threshold 0.5409877865338792; echo "exit=$?"
```

The recorded outcomes are 65% before (exit 1) and 100% after (exit 0). State that this
expanded-set score is in-sample because the added questions were selected from uncovered
live-query topics.

## F — Kubernetes runtime and release evidence

Every F screenshot must be captured against your running `ragops-dev` profile. Confirm
the context before collecting anything:

```bash
echo F0
kubectl config current-context
```

**F1 — inventory** (include all resource kinds requested in the brief):

```bash
echo F1
"${k[@]}" get all,pvc,configmap,cronjob,job -o wide
```

**F2 — completed ingestion Job logs:**

```bash
echo F2
"${k[@]}" get jobs
"${k[@]}" logs job/ingest
```

**F3 — completed evaluation Job logs and gate outcome:**

```bash
echo F3
"${k[@]}" get jobs
"${k[@]}" logs job/eval
```

If you used different Job names, substitute the completed run's actual names.

**F4 — ConfigMap-only gate flip:** capture the active threshold, edit one threshold,
rerun the evaluation Job, and show the changed result. Do not rebuild the image. Record
the original ConfigMap values first so you can restore them afterward.

```bash
echo F4-before
"${k[@]}" get configmap gate-config -o yaml
```

Use `kubectl --context ragops-dev -n ragops edit configmap gate-config` to change a
threshold (for the recorded strict demo, set `p95_latency_baseline_factor: 0`), then
delete and recreate the eval Job from the manifest and show its logs:

```bash
"${k[@]}" delete job eval --ignore-not-found
"${k[@]}" apply -f k8s/eval-job.yaml
"${k[@]}" wait --for=condition=complete job/eval --timeout=40m || "${k[@]}" wait --for=condition=failed job/eval --timeout=40m
"${k[@]}" logs job/eval
```

For a failing gate, the Job is expected to fail, so the `||` branch waits for its
failed condition. Restore the exact original ConfigMap from `k8s/config.yaml` with
`kubectl --context ragops-dev -n ragops apply -f k8s/config.yaml`, delete/recreate the
Job, and capture the restored gate result. No image rebuild is involved.

**F5 — rollout, undo, and a post-undo trace:**

```bash
echo F5-rollout
"${k[@]}" rollout status deployment/api --timeout=5m
"${k[@]}" rollout history deployment/api
```

For the controlled bad release, set the measured bad top-k/collection configuration
and wait for rollout before undoing it. Then query the API again and rebuild the trace.
The final trace must show the collection and embedding version restored by undo.

```bash
echo F5-undo
"${k[@]}" set env deployment/api CHROMA_COLLECTION=rahbar_kube_v1_nomic CHUNK_SIZE=400 TOP_K=1
"${k[@]}" rollout status deployment/api --timeout=5m
"${k[@]}" rollout undo deployment/api
"${k[@]}" rollout status deployment/api --timeout=5m
```

Start the API port-forward in another terminal, issue the same query as D1, extract its
new trace ID, and run `python -m ragops trace "$trace_id"` inside the API pod as in D2.
Use the new post-undo trace ID, not a historical trace.

## Human review before submission

The current golden file has eight human-authored questions, but the 26 synthetic
questions are not human reviewed. A team member must check at least eight synthetic
rows against the pinned source document/page, then update both `eval/golden.jsonl` and
`eval/golden_expanded.jsonl` consistently: set `reviewed` to `true`, set
`review_status` to `human_reviewed`, and identify the human reviewer in `notes`.
Record which IDs were checked in [GOLDEN_REVIEW.md](../eval/GOLDEN_REVIEW.md). Do not
mark Codex's checks as human review.
