# RAHBAR Work Log

This file tracks implementation against the assignment. It records concise decision
summaries, assumptions, verification evidence, and remaining work. It is an engineering
record, not private internal reasoning.

## Working rules

- Work in the connected local folder only. Do not push or publish changes.
- Keep `main` untouched. The `.git` directory is read-only in this workspace, so creating
  a local Git branch is not available here; source files in this folder are writable.
- Do not claim cluster, CI, corpus, or runtime evidence until it has actually been produced.
- For assumptions, prefer reversible choices and mark items requiring the team's decision.
- Assignment deadline: 8 November 2026, 23:59 PKT.

## Status summary

| Area | Status | Evidence / next action |
| --- | --- | --- |
| Starter kit and repo orientation | Done | Read `STARTER.md`; repo is still the starter kit on `main`. |
| Kubernetes around stubs | Scaffold drafted; runtime pending | Dockerfiles and dev/prod Kustomize resources are present. `kubectl kustomize` rendered both overlays successfully. Need cluster deployment, image build, probe checks, endpoints, rollout/undo, policy tests, and resource measurements. |
| RAG extraction, cleaning, chunking, embedding, storage | Implemented draft; verification pending | Five stages drafted; need parser/chunker tests and real fixture run. |
| API retrieval, generation, cache, abstention, readiness and metrics | Implemented draft; verification pending | Chroma, providers, Redis cache, citations, fallback, readiness and metrics drafted; need API tests and runtime checks. |
| Corpus | Downloaded; properties pending | Nine sources downloaded locally and hashes generated. Page count, OCR/font scan, table/definitions checks, and golden passages still need verification. |
| Evaluation | Not started | Golden set before tuning, metrics, baseline and CI gate. |
| Kubernetes and CI/CD evidence | Not started | Requires usable local cluster and GitHub Actions credentials/settings. |
| Assignment documentation | In progress | Added README, architecture, ADR 0001, AI disclosure, and this tracker; fill corpus, pipeline, failure, engineering notes and remaining ADRs from observed work. |

## Decisions and assumptions

| Date (PKT) | Decision / assumption | Why | Revisit when |
| --- | --- | --- | --- |
| 2026-11-05 | Use the connected Downloads folder as the working copy; make no GitHub writes. | User explicitly connected this folder and said to work locally only. | If the user connects a different folder or asks to publish. |
| 2026-11-05 | Follow the assignment's staged plan: Kubernetes around stubs first, then real RAG. | The assignment deliberately allocates the first half of the week to cluster plumbing. | If the team/instructor has approved a different order. |
| 2026-11-05 | Record rationale as concise decision summaries rather than private chain-of-thought. | Keeps the log useful and auditable without exposing hidden reasoning. | Never. |

## Work entries

### 2026-11-05 — repository handoff

- Confirmed current folder is the RAHBAR starter repository, clean on `main`, with the
  GitHub remote set to `momnakhan24/rahbar`.
- No source files have been edited yet.
- Attempted to create local branch `codex/assignment-implementation`; Git could not write
  `.git/refs` because Git metadata is read-only in this workspace. No branch or remote was
  changed at that time. Later the user approved granular local commits and Git metadata
  write access; the work was moved to branch `dev` without changing the remote.
- Read `STARTER.md` and key API/indexer configuration. The repository has no Dockerfiles,
  Kubernetes manifests, workflows, or real corpus manifest; many core functions remain
  starter stubs.

### 2026-11-05 — milestone 1: stub-mode deployment scaffold

- Added API, indexer, and UI Dockerfiles. Python images pin Python 3.12.8; nginx is
  unprivileged; Python containers run with a dedicated UID.
- Added namespace, ConfigMap, workload ServiceAccounts, four ClusterIP Services, API/UI
  Deployments, Chroma StatefulSet with volumeClaimTemplates, Redis Deployment with PVC,
  dummy indexer Job and weekly CronJob, Ingress, CPU HPA, and default-deny NetworkPolicies.
- Added dev/prod overlays, README clean-clone order, architecture overview, ADR 0001, and
  the AI-assistance disclosure.
- **Assumptions:** dev uses starter stubs and the `dummy-768` index; local image tags are
  `dev`; production image names/tags are placeholders for the later CI workflow. The host
  Ollama NetworkPolicy CIDR is set to the common Minikube Docker gateway
  `192.168.49.1/32`, which must be checked and adjusted for the actual cluster.
- **Provisional values:** CPU/memory requests and limits have not been measured. They must
  not be described as justified until `kubectl top pods` evidence is collected.
- **Verification:** `kubectl kustomize k8s/overlays/dev` and `kubectl kustomize
  k8s/overlays/prod` both rendered successfully. No images were built and no cluster was
  started. Docker Desktop's CLI is present; Minikube is unavailable in the connected
  environment, so runtime evidence is still open.

### 2026-11-05 — milestone 2: real pipeline and API draft; corpus retrieval

- Implemented PDF, HTML, Markdown, and text extraction; page-level OCR when PDF text is
  missing; PDF table-row serialization; repeated header/footer cleanup; structure-aware
  word-token chunking with overlap; batched Ollama embeddings; and Chroma versioned index
  publication through a registry collection. The indexer flushes the Redis DB after
  switching the active generation so cached answers do not survive re-indexing.
- Implemented query embeddings, current-version metadata filtering (including a heuristic
  for explicit historical questions), Ollama JSON-schema output, OpenAI-compatible hosted
  JSON-schema output, Pydantic citation validation with one retry and a safe fallback,
  relevance-floor abstention, Redis semantic cache, and Chroma/Redis/model-pin readiness.
- Added Prometheus counters/histograms for retrieval and generation latency, cache hits,
  abstentions, fallbacks, and estimated token input/output. Token values currently use a
  documented character/4 estimate and have not been compared to provider usage fields.
- Copied the suggested FAST-NUCES source list to `corpus/sources.yaml`; all nine listed
  URLs returned a document/page. `corpus/MANIFEST.md` and local ignored `corpus/raw/` were
  generated. The old 2023 policy, current handbook, prospectus rules, Student Handbook,
  two annual reports, fees/grading pages, and likely scanned policy are included.
- **Assumptions:** the source list follows the assignment's suggested institution and
  starter source list; semantic cache starts at `0.96`, relevance floor at `0.35`, and
  chunking at 400/50 whitespace words. These are provisional only; the assignment requires
  measured threshold and chunk-size experiments.
- **Verification:** source downloads and manifest hashes completed. Python 3.13 venv
  creation succeeded; dependency installation was interrupted after repeated DNS errors
  to `files.pythonhosted.org`. No test suite, submission checker, OCR run, page-count
  audit, or live Chroma/Redis/model run has completed. Minikube is unavailable.
- **Next:** install dependencies when network access is available, run tests/lint/checker,
  inspect all nine documents for pages/OCR/tables/version pair, then finish corpus and
  evaluation artifacts. Keep actual cluster and CI evidence explicitly pending.

### 2026-11-05 — local commit organization

- Created local branch `dev` after the user explicitly requested it and granted the
  required `.git` write access.
- Committed each of the 50 changed assignment files in its own commit with a
  path-specific message. This keeps every commit limited to one file/change for review.
- No remote push, PR, merge, or publication was performed. The commits exist only in the
  connected local repository.

## Remaining requirements checklist

The checklist below will be expanded and updated as each requirement is implemented and
verified. “Done” requires evidence; source code alone is not runtime evidence.

- [ ] Corpus properties and provenance (`docs/CORPUS.md`, manifest, fetch script, hashes).
- [x] Implement extraction, OCR fallback, cleaning, structure-aware chunking, embedding
  pin plumbing, and versioned Chroma storage; [ ] verify with actual corpus and tests.
- [ ] Three measured chunk configurations and recall@5 comparison.
- [x] Implement API top-k retrieval with current-version filtering and embedding pin
  readiness guard; [ ] verify with live Chroma and mismatch demonstration.
- [x] Implement schema-constrained generation, citation validation, retry/fallback,
  abstention; [ ] add tests and verify with a real/stubbed provider.
- [x] Implement Redis semantic cache, safe exclusions, and re-index invalidation; [ ] tune
  threshold from data, add tests, and complete cache ADR.
- [x] Kubernetes manifests scaffold namespace, deployments, StatefulSet Chroma, persistent
  Redis, index Job/CronJob, four ClusterIP services, ingress, HPA, network policies,
  security contexts and resource requests/limits.
- [x] Container image definitions and dev/prod Kustomize overlays; both overlays render.
- [ ] Build images and verify all workload probes, readiness, storage, endpoint count,
  rollout/undo, policy behavior, HPA metrics, and measured resource values on a cluster.
- [ ] Structured logs and required Prometheus metrics.
- [ ] At least 15 golden questions, recall@3/5, citation validity, abstention check and baseline.
- [ ] Four deliberate failure analyses with diagnostics and remedies.
- [ ] CI lint/test/coverage/manifests/build/scan/e2e gate and gated CD by SHA.
- [ ] Required engineering notes, ADRs, README, AI disclosure, screenshots/evidence.
- [ ] Run checker and available automated tests; document external/runtime blockers precisely.
