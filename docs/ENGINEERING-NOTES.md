# Engineering notes

Answers below refer to this repository's implementation and distinguish design behavior from measurements. Until a Kubernetes cluster and Ollama runtime are available, live timings, peak memory, HPA response and real-corpus recall are not reported as observed facts.

## 1. Why must indexing stay out of API startup?

With three API replicas and one Chroma volume, startup indexing creates three competing writers. Restarts can repeat expensive OCR/embedding work and expose a partially written collection while another pod is querying. The API startup path only constructs serving dependencies; extraction, chunking, embedding and publication are in `indexer/pipeline/run.py` and run as a Kubernetes Job. The Job uses `backoffLimit: 2`; versioned collection publication keeps an incomplete generation from becoming active.

## 2. What if readiness and liveness are swapped while Chroma is slow?

Liveness should answer whether the process can continue. `/healthz` intentionally touches no dependency. Readiness at `/readyz` checks that Chroma has a non-empty active collection with the expected embedding model and that Redis responds. If slow Chroma were wired to liveness, Kubernetes would restart otherwise healthy API processes during a dependency slowdown, increasing load and causing a restart loop. If readiness only checked process health, broken pods would continue receiving traffic. Keep dependency checks in readiness and tune its timeout/failure window to the measured cluster behavior.

## 3. What does CPU HPA measure, and what should scale generation?

The HPA in `k8s/base/hpa.yaml` requests 3–8 replicas and targets 70% average CPU utilization relative to CPU requests. CPU is a useful signal for tokenization, JSON handling and some provider clients, but hosted generation may spend most request time waiting on network/model latency. Queue depth, concurrent in-flight generations, request latency and provider saturation would better describe user demand. A production system should export those signals and use a custom/external metric; this assignment's CPU policy is the available baseline until measurements justify a change.

## 4. Indexer peak memory, limit, margin and exit behavior

The indexer container currently requests 512 MiB and has a 2 GiB limit in the Job and CronJob manifests. The source accumulates all chunks and vectors before publication, so corpus size and OCR image conversion can create a meaningful peak. No `kubectl top` or cgroup peak measurement has been collected, so the memory margin is **unknown** and 2 GiB is a provisional ceiling, not a measured safe limit. A failure raises/returns non-zero; Kubernetes retries up to two times. Measure peak memory during a full corpus run, then set request near representative use and limit with an explicit safety margin.

## 5. Recall@5 by question type

No real-corpus evaluation has run, so there is no defensible measured worst category. Likely risk areas are scanned/OCR policy questions, historical-version comparisons, exact terms and questions about omitted hostel application procedures. These are hypotheses based on corpus properties, not results. `eval/run_eval.py` reports recall@5 by type; populate `eval/results.json` from the real corpus before choosing a remediation. OCR and historical questions need particular review because the 2023 rules are mostly scanned.

## 6. What happens if API EMBED_MODEL changes alone?

The readiness route reads the active Chroma registry collection's `embed_model` metadata and compares it with `settings.embed_model`. A mismatch makes `/readyz` return HTTP 503 and logs `embedding model conflict`; `/healthz` remains live. This prevents traffic from being served with semantically incompatible query vectors. Restore the API pin or reindex/publish with the new model before returning to ready. The collection metadata records the name, but a model version/digest would be a stronger pin for mutable tags.

## 7. The failure that cost more than an hour

The largest observed failure so far was environmental rather than an application incident: dependency installation initially failed because the sandbox could not resolve the Python package host, and the local Docker CLI could not reach the Docker Desktop Linux engine. Dependencies were later installed after explicit network approval, allowing unit tests and static checks, but there is still no cluster evidence. The lesson is to validate local prerequisites early and record failures precisely; do not substitute rendered manifests or unit tests for rollout, HPA or resource evidence. The work log records the remaining blocked deployment checks.

## Measurements to add before submission

Capture `kubectl top pods -n rahbar --containers`, `kubectl get hpa -n rahbar`, endpoint and rollout output, plus before/after readiness and rollback checks. Record the actual command, timestamp, cluster profile, image SHA and result under `docs/evidence/`. Do not fill unknown memory, recall or latency values with estimates presented as measurements.
