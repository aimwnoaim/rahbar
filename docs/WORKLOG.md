# RAHBAR assignment work log

This log is the reviewable record of implementation, verification, assumptions and remaining work for Assignment 02. It records concise engineering rationale and evidence, not private chain-of-thought. Status labels distinguish code that exists from behavior actually observed in a running system.

## Working rules

- Work only in the connected repository. Push only when the user explicitly authorizes it; do not merge or open a PR unless asked.
- Keep all assignment changes on the user-requested local `dev-aimwnoaim` branch; keep each commit limited to one file/change.
- The configured local Git author for new commits is `momnakhan24 <i243119@isb.nu.edu.pk>`. Earlier commits remain under their original authors; they were not rewritten. This sets commit attribution fields only and does not log into, impersonate, or grant access to a GitHub account. GitHub attribution depends on its account/email verification.
- Record unknowns as unknown. Source code and rendered YAML are not evidence of a live rollout, measured retrieval quality or protected-branch behavior.
- Assignment deadline from the handout: 8 November 2026, 23:59 PKT.

## Current status

| Requirement area | Status | What is verified / still needed |
| --- | --- | --- |
| Local branch and commit organization | Implemented and pushed | Branch `dev-aimwnoaim`; commits are one file/change each. The user authorized pushing the five local commits on 2026-11-05; local HEAD now matches origin. |
| Kubernetes stub deployment | Manifests and smoke workflow prepared | Both Kustomize overlays render. Docker Desktop engine is unavailable here; no image build, cluster rollout, probes, endpoints, HPA behavior or rollback was observed locally. CI workflow has not run on GitHub. |
| Corpus and provenance | Audited | Nine listed documents and SHA-256 manifest; seven PDFs total 279 pages, plus two HTML pages. Detailed audit is in [`CORPUS.md`](CORPUS.md). Raw files are ignored and not committed. |
| Extraction, cleaning, chunking, embedding and store | Implemented; unit-tested in parts | PDF/HTML/Markdown/text parsing, OCR path, cleanup, structure-aware chunks, Ollama embeddings and staged versioned Chroma publish are implemented. 9 indexer tests pass. Full corpus indexing, OCR quality review and live vector-dimension evidence remain. |
| API retrieval, provider, citations, abstention and cache | Implemented; unit-tested | Chroma retrieval, provider interface, schema validation/retry/fallback, relevance-floor abstention, Redis semantic cache and readiness pin guard are present. 13 API tests pass. No live Chroma, Redis or model requests have been run. |
| Golden evaluation | Set and scoring code present; real metrics pending | `eval/golden.yaml` contains 17 real-corpus questions; evaluator reports exact expected-term accuracy in addition to recall/citations/abstentions. `eval/baseline.json` is an explicit pending marker with null recall, so the regression gate correctly fails. No measured `results.json` exists. Real evaluation remains blocked on indexing/model/cluster access and OCR review. |
| Assignment documentation and ADRs | Drafted and mapped | Corpus, pipeline, six failure-analysis plans, seven engineering answers, AI disclosure, architecture, and four ADRs are present. Fault-injection plans are not reported as observed incident evidence. |
| CI/CD | CI passed on daff3ae | Run 42083260429 passed quality and cluster smoke, including all three image scans, workload rollout, indexer completion, and the question endpoint. This exercises the dev stub path; real corpus/model evaluation, production CD, registry publication and GitHub protection evidence remain open. |
| Evidence bundle | Not complete; capture runbook prepared | [`OPERATIONS.md`](OPERATIONS.md) gives exact commands and evidence names. No real branch protection screenshot, blocked-merge evidence, `kubectl top`, endpoint/HPA output or rollout/failure evidence is available; these require GitHub settings and a working cluster. |

## Decisions and assumptions

| Date (PKT) | Decision / assumption | Reason and limits |
| --- | --- | --- |
| 2026-11-05 | Use the connected repository at `C:\Users\HP\Downloads\rahbar-starter\rahbar-starter`; do not push. | The user connected this folder and explicitly requested local-only work. |
| 2026-11-05 | Push the five committed changes on `dev-aimwnoaim` to origin. | The user explicitly authorized the push on 2026-11-05 after the local commits were reviewed. Push succeeded; no merge or PR was created. |
| 2026-11-05 | Continue on branch `dev-aimwnoaim` and make one file/change per commit. | Explicit user instruction. Each new commit is independently reviewable. |
| 2026-11-05 | Use the user-provided alternate account name/email only as local Git author metadata for new commits. | The user identified it as their own repo-owner account. Existing commits are not rewritten; no credentials or authenticated GitHub access were provided. |
| 2026-11-05 | Use FAST-NUCES public documents from the starter source list. | Fits the assignment source and enables plausible exact-term and abstention questions. Web pages can change; manifest hashes establish the retrieved bytes. |
| 2026-11-05 | Keep current rules as default and permit superseded chunks only when a question asks historically. | Prevent accidental citation of old policy. Historical retrieval still needs a live, reviewed version-pair evaluation. |
| 2026-11-05 | Use 400/50 approximate word chunks, cache cutoff 0.96, and relevance floor 0.35 provisionally. | Defaults are implementation values, not tuned results. Three chunk sizes, threshold sweeps and false-hit checks have not been run. |
| 2026-11-05 | Do not fabricate baseline values, resource measurements or evidence screenshots. | They are empirical assignment deliverables and require access to the live runtime/settings. |

## Work completed

### Kubernetes scaffold and deployment path

- Added pinned API/indexer/UI Dockerfiles, non-root users, exec-form commands, `.dockerignore` rules, Namespace, Services, Deployments, Chroma StatefulSet/PVC, Redis/PVC, indexer Job/CronJob, Ingress, HPA, service accounts and default-deny/allow NetworkPolicies.
- Added dev and prod overlays. Dev patches the indexer to dummy mode; prod selects Chroma retrieval, `ollama-host`, and `nomic-embed-text`, and the base Job runs the actual pipeline.
- Added a persistent corpus PVC and temporary loader Pod example excluded from Kustomize. The README documents corpus copy, one-shot indexing and rollout order. The placeholder Secret is documentation only and is not applied; real secrets are created with `make secret`.
- Updated capability-drop syntax and UI image command after mechanical checking.
- **Verification:** `kubectl kustomize k8s/overlays/dev` and `kubectl kustomize k8s/overlays/prod` both exit successfully after the current manifest changes. No Kubernetes API server validation or live workload was available.
- **Environment blocker:** Docker CLI exists, but `docker info` cannot connect to Docker Desktop's Linux engine. Minikube, kind, Tesseract and Poppler are unavailable in this environment. Do not claim cluster, image, OCR or resource evidence.

### Pipeline, API and corpus

- Implemented PDF/HTML/Markdown/text extraction; OCR fallback on pages with under 25 normalized text characters; PDF and HTML table serialization; repeated page-furniture cleanup; section-aware word chunking with overlap; batched Ollama embeddings; versioned Chroma collection publication and registry switch.
- Implemented Chroma query embeddings, current-version filtering, historical question heuristic, Ollama and OpenAI-compatible provider classes, schema-constrained JSON, Pydantic validation, one retry, validated citation membership, fallback and low-relevance abstention.
- Implemented Redis semantic cache with model/revision-scoped keys, seven-day TTL, follow-up and abstention exclusion, re-index invalidation and a deterministic character/4 token estimate in metrics. Cache threshold remains unmeasured.
- Readiness checks active Chroma collection count, configured/indexed embedding model and Redis; liveness avoids dependencies. Structured logs and Prometheus metrics are implemented.
- Downloaded nine public sources locally; verified source hashes and audited PDF pages. The 2022 entrepreneurship policy has 8 image-only pages; the 2023 undergraduate rules have 24 of 26 pages with negligible text. OCR execution and manual accuracy review remain open.
- Added 17 real-corpus golden questions covering ordinary, exact, current-version, must-abstain and instruction-injection cases. Relevant sections are based on the current 2026 handbook and parser's `Document` heading for HTML.
- Evaluation output also reports literal expected-term match accuracy for questions with an `expect` value; this is a diagnostic metric and does not replace human answer review.

### Tests and static validation

- API tests: 14 passed, including citation validation/fallback, abstention, semantic-cache revision pruning, prompt-injection handling and embedding-model mismatch behavior.
- Indexer tests: 9 passed, covering Markdown front matter, HTML tables, repeated headers, chunk overlap/metadata and invalid configuration.
- Evaluation tests: 4 passed, covering recall matching, citation validity, abstention and score gates.
- Ruff: `ruff check api indexer eval corpus` passed.
- API mypy: `mypy app` passed with no issues in 23 source files.
- Indexer mypy passed: no issues found in 10 source files.
- The latest submission-checker run reported 162 passes, 3 warnings and 1 failure. The sole failure is the five-file evidence bundle (branch protection, blocked merge, `kubectl top`, endpoints and HPA). Warnings are the placeholder Secret heuristic, 44% conventional commit prefixes, and missing measured `eval/results.json`. The baseline file is intentionally a pending marker; it is not reported as a measured baseline.
- The most recent full test runs passed: API 14, indexer 9 and evaluation 4. Ruff passed; API mypy reported no issues in 23 files; indexer mypy reported no issues in 10 files. Both Kustomize overlays rendered successfully.
- README now lists the GitHub Environment, secrets, variables, required checks and registry image prerequisites for the manual CD workflow. Those external settings have not been configured from this local-only workspace.
- Added [`OPERATIONS.md`](OPERATIONS.md) with safe cluster, rollback, failure-injection, GitHub protection and evidence-capture steps; it is a runbook, not evidence of those operations.
- Investigated the uploaded Trivy CI log. The failing gate was scanning `rahbar-api:dev`: Debian packages had HIGH/CRITICAL findings and the installed Starlette 0.46.2 had three HIGH findings. It was a vulnerability scan failure, not a Docker socket failure.
- Updated API and indexer Dockerfiles to Python 3.12.16 slim Trixie and refresh OS packages at build time; upgraded FastAPI and pinned Starlette to 1.7.0; configured the three Trivy image scans to fail on HIGH/CRITICAL vulnerabilities that have fixes while omitting unfixable findings. These changes are local commits `82e712c`, `22a58aa`, `931c004`, and `c703d7f`, each limited to one file.
- After dependency update, API tests passed (14), API mypy passed (23 source files), and Ruff passed for `api indexer eval corpus`. The dependency installation resolved successfully. GitHub Actions has not yet run against these commits, so the scan result is not verified as fixed remotely; the UI image scan may reveal separate findings when CI progresses.
- Pushed the five remediation/documentation commits to `origin/dev-aimwnoaim` after explicit user authorization. GitHub's combined status endpoint currently returned no check entries, so CI completion remains unverified.
- Retrieved the latest push-triggered CI run `41995169603`. The quality job passed; in `cluster-smoke`, the API image and indexer OS scan had zero high/critical findings, while the indexer Python scan failed on 22 HIGH findings: `pypdf==5.4.0` and transitive `pdfminer.six==20250327`. The job stopped there, so the UI scan was not reached.
- Upgraded the indexer parser stack to `pdfplumber==0.11.10`, `pypdf==6.21.4`, and `pdfminer.six==20260107`, which satisfy the fixed versions identified by Trivy. These dependency pins install together successfully. Indexer tests pass (9); the CI mypy command `cd indexer && mypy pipeline` passes with no issues in 10 files. This CI fix is committed locally as `86a60a7`; the follow-up workflow run is still needed to verify the scan and UI image.
- Follow-up CI run `42075533976` passed its quality job and cleared API/indexer scans, then failed at the UI scan with 63 HIGH/CRITICAL OS findings from the older NGINX Alpine base. Updated the UI image to `nginxinc/nginx-unprivileged:1.31.7-alpine3.24` and refresh Alpine packages during build. This is committed as `3459cf3`; a new CI run is required to verify the UI scan and smoke deployment.
- CI run `42076546169` passed quality and all three Trivy scans (API, indexer, UI). The cluster job timed out waiting for `statefulset/chroma`'s `chroma-0` pod. Added a 90-second readiness check and failure diagnostics (`get/describe`, container logs and events); run `42078459739` showed the container panicking during SQLite migration with extended error 6410. This corresponds to SQLite failing to find a usable temp directory; SQLite checks `SQLITE_TMPDIR`/`TMPDIR` and standard temporary paths on Unix ([SQLite temporary files](https://www.sqlite.org/tempfiles.html)). Added a writable `emptyDir` at `/tmp` plus `SQLITE_TMPDIR=/tmp` and `TMPDIR=/tmp`, retaining the read-only root filesystem. Manifest rendering passes; commit `082e935` awaits CI validation.
- CI run `42079830021` verified that Chroma no longer panicked, but diagnostics showed `Listening on localhost:8000`; readiness probes to the pod IP were refused. Added `--host 0.0.0.0` to the Chroma command so the service can accept pod-network connections. `kubectl kustomize` renders both dev and prod overlays. This fix is committed as `f1fe2e3`; CI validation remains pending.

## Assignment completion checklist

- [x] Build K8s scaffold for API/UI/Chroma/Redis and separate Job/CronJob indexing; dev/prod overlays render.
- [x] Provide container definitions, non-root execution, probes, resource requests/limits, security contexts, ingress, autoscaling and network policies.
- [x] Implement extraction/OCR fallback, cleaning, chunking, embedding pin metadata and versioned vector-store publication.
- [x] Implement grounded API retrieval, source/version filters, citation checks, retry/fallback, abstention, cache and readiness guard.
- [x] Provide corpus manifest and document required source properties; record scan/table/absent-topic evidence.
- [x] Add test suites, prompt-injection probe, 17-question real-corpus golden set and evaluation scoring/gate code.
- [x] Write four ADRs, architecture/AI disclosure, pipeline, corpus, failure-analysis plans, engineering notes and local work log.
- [x] Prepare CI and manual SHA-based CD workflows locally; address the uploaded API Trivy failure in four one-file local commits.
- [ ] Run GitHub CI against the local remediation commits and review any subsequent indexer/UI scan failures.
- [ ] Establish and commit a measured baseline/results after real corpus indexing and model evaluation; run chunk-size and cache-threshold experiments.
- [ ] Execute OCR and manually review scan output, especially the 2023 rules and 2022 policy.
- [ ] Build images and run dev cluster; capture API/UI endpoints, probes, readiness mismatch, rollout/undo, HPA and NetworkPolicy evidence.
- [ ] Run four deliberate failure experiments and replace planned procedures with timestamped actual diagnostics/remedies.
- [ ] Configure GitHub environment protection/secrets, run CI/CD, and capture branch protection plus blocked-merge evidence.
- [ ] Re-run full submission checker and resolve remaining evidence-dependent issues before submission.

## Next actions

1. Run `docker info`, start Docker Desktop, and provision Minikube with Calico; otherwise use a cluster with equivalent ingress/metrics support.
2. Fetch/verify the corpus and load `corpus/raw` into `corpus-data` using the temporary loader workflow. Run the real indexer and verify Chroma active revision/model metadata.
3. Install/run Tesseract and Poppler through the indexer image, review OCR pages, and correct source metadata/golden sections if needed.
4. Execute golden evaluation and chunk/cache sweeps; write only actual results to `eval/baseline.json` and `eval/results.json`.
5. Capture evidence files from the actual cluster and GitHub settings; configure the protected production environment and required repository variables/secrets.
6. Run `make check`, full tests, lint and type checks. Review the local commit list; do not push unless the user later authorizes it.

### CI follow-up: indexer startup

- Run 42081591091 passed quality and all image scans. Chroma and Redis became ready; the indexer Job did not complete within five minutes. Its logs were not captured by that workflow.
- Added a bounded 60-second Chroma heartbeat wait before creating the indexer client (e1a81f8). This addresses an identified startup race; the failed Job's exact cause is not yet confirmed.
- Added workload descriptions, current/previous container logs, and events on failure (8f92cd1). Indexer tests: 9 passed; Ruff passed. Next CI run will validate the wait and reveal any remaining failure.

### CI verified passing

- GitHub Actions run [42083260429](https://github.com/momnakhan24/rahbar/actions/runs/42083260429) on commit `daff3ae` completed successfully: both `quality` and `cluster-smoke` passed.
- Observed checks include lint/type checks, unit/evaluation-gate tests, manifest validation, image builds, all three Trivy gates, Chroma/Redis/API/UI rollout, dummy indexer Job completion, and HTTP question endpoint smoke test.
- The bounded Chroma connection wait cleared the remaining indexer startup failure. Each implementation/workflow change and its log update was committed separately. This is evidence for the dev stub CI path, not real-model retrieval quality or a production deployment.

### Full assignment execution started

- User authorized Minikube installation and completing remaining assignment work; Docker Hub namespace: `aimwnoaim`.
- Docker Desktop Linux engine responds with version 29.8.0. Installed Minikube 1.39.0 through the official Winget package. Provisioning isolated profile `rahbar` with Docker, Calico, 4 CPUs, 4096 MB, metrics-server and ingress; other running projects are left intact.
- Local immutable image builds and a local Ollama model service download are underway. No new live evaluation results are claimed yet.
- Re-read the assignment: the existing CI smoke path does not yet satisfy fixture retrieval evaluation, and existing manual CD does not satisfy the required push-to-main test/build-push/deploy chain. These gaps must be addressed, in addition to real evaluation, experiments and evidence.
- Submission checker currently reports 162 passes, 3 warnings and 1 evidence-bundle failure; passing that checker alone is not assignment completion.
- Implemented CD test → build-push → ephemeral acceptance deploy with `needs:`, SHA tags, Trivy and Ingress smoke verification (a862192). It triggers on main or manual dispatch and uses Docker Hub namespace aimwnoaim plus repository secret DOCKERHUB_TOKEN. YAML parsing passed; publication/deployment remains unverified until credentials and a workflow run are available.
- Added scripts/measure_pipeline.py for cached extraction/OCR inventories and measured 250/30, 400/50, 600/75 chunk sweeps using real embeddings and exact cosine retrieval. It explicitly separates retrieval-only experiments from API generation evaluation. Script compiles and Ruff passes; experimental values are pending execution. Ignored work/ for intermediate extraction/vector data.
