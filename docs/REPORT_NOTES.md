# Assignment 03 — RAGOps report notes

## Cover page

**Project** RAHBAR, FAST-NUCES policy question answering  
**Member 1** [Name] · [Roll number]  
**Member 2** [Name] · [Roll number]

## Figure 3 lifecycle mapping

| Stage | Implementation | Evidence or open item |
| --- | --- | --- |
| Ingest | Stage the pinned corpus and source manifest, then extract pages. | `scripts/stage_ragops_batch_a.py`, `ragops/ingest.py` |
| Verify | Record quality, completeness, recency and uniqueness. Flag suspicious instructions. | `ragops/verify.py`, verification reports |
| Update data lake | Preserve raw revisions and maintain an active manifest, quarantine, archive and restore. | `ragops/lake.py`, unit tests |
| Update retrieval sources | Reconcile document versions, chunk hashes, access and status with Chroma. | `ragops/index.py`, incremental results |
| Offline testing | Compare embedding, retrieval and end-to-end results over seeded repeats and noise. | `ragops/evaluation.py` |
| Live testing | Evaluate the candidate Service and enforce the gate before rollout. | `k8s/eval-job.yaml`, `k8s/README.md` |
| Check coverage | Compare live queries with golden queries and group uncovered topics. | `ragops/coverage.py`, coverage calibration and reports |

## Quality attributes

| Attribute | Measure | Threshold or evidence |
| --- | --- | --- |
| Adaptability | Changed document and chunk counts | An unchanged ingestion should embed zero chunks. |
| Monitorability | Top-result similarity, abstention rate and latency by stage | `/metrics`, `python -m ragops metrics` |
| Observability | Dropped suspicious retrievals, supported citations and cache outcomes | Trace entries and per-question evaluation details |
| Traceability | Exact prompt hash, model revision, source version and access filters | `python -m ragops trace TRACE_ID` |
| Reliability | Index orphan scan, PVC recovery and rolling update availability | Incremental results, fresh-cluster evidence pending |

## A. Verification and incremental indexing

| Run | Seen | New | Changed | Quarantined | Embedded | Deleted chunks | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Full Batch A | 10 | 8 | 1 | 1 | 724 | 0 | [Verification](../eval/results/verification_report_20261123T193246Z-8e991eba.json), [incremental](../eval/results/incremental_20261123T193246Z-8e991eba.json) |
| Batch B against authored Batch A fixture | 11 | 5 | 1 | 5 | 6 | 1 | [Verification](../eval/results/verification_report_20261123T194050Z-9cf18ab7.json), [incremental](../eval/results/incremental_20261123T194050Z-9cf18ab7.json) |
| Unchanged authored fixture | 1 | 0 | 0 | 0 | 0 | 0 | [Incremental](../eval/results/incremental_fixture_unchanged.json) |

The full Batch A run flagged the 2023–24 annual report as a near duplicate of the 2019–20 report at cosine 0.951385. The report titles identify different periods. This is a likely false positive from shared structure and boilerplate. [Full Batch A verification](../eval/results/verification_report_20261123T193246Z-8e991eba.json)

With the fixture inbox changed to remove the locker policy, reconciliation deleted its chunk and found no orphans. The restored recorder revision then replaced the active chunk. [Deletion](../eval/results/incremental_20261123T195520Z-6e4d692a.json), [restore](../eval/results/restore_fixture.json)

## B and C. Evaluation and release

The three-level evaluation, noise, seeded differences and candidate decision require completed baseline and candidate result files. The configured thresholds are in `config/gate.yaml`. Release status is pending.

## D. Observability

The trace saves retrieved text, ranking, rail actions, filtered generation context and the complete Ollama request bodies.

1. Trace `749f8d0a2517460abd1b713da4956327` asks where the recorder return locker is.
2. The top retrieval is the locker policy in the Batch B fixture.
3. The retrieval rail drops that chunk for an instruction-pattern match.
4. The other retrieved chunks fall below the relevance floor, leaving an empty generation context.
5. The trace records an abstention and no model requests. [Fixture trace](../traces/batch-b-fixture.jsonl)

## E. Coverage and distribution change

The calibration computes the midpoint between the mean cosine scores of paraphrase and unrelated pairs. The initial exploratory threshold of 0.78 yielded 25% coverage before expansion and 62.5% after expansion. Both were below the paper's 85% example. [Calibration](../eval/results/coverage_calibration.json), [exploratory before](../eval/results/coverage_20261123T194246361873Z.json), [exploratory after](../eval/results/coverage_20261123T194439618413Z.json)

At the calibrated cutoff of 0.540988, coverage was 65% before expansion and 100% afterward. The original set returned exit code 1 and the expanded set returned 0. The expanded set deliberately targets uncovered live topics, including abstention for unsupported topics. Its coverage is an in-sample demonstration. [Calibrated before](../eval/results/coverage_20261123T194748858957Z.json), [calibrated after](../eval/results/coverage_20261123T194915958965Z.json)

## F. Kubernetes

The fresh `ragops-dev` Minikube profile bound the data, model and Chroma PVCs. Fixture ingestion ran in the Kubernetes Job. Live and candidate Deployments reached readiness, the API rejected a write attempt, and the fixture chunk survived a Chroma pod restart. The Kubernetes workloads called the pinned local Ollama through a temporary relay while the in-cluster Ollama image pull was stalled. [Ingest Job](../eval/results/k8s_fixture_ingest.json), [API write rejection](../eval/results/k8s_api_readonly.txt), [persistence](../eval/results/k8s_chroma_persistence.txt)

| Workload | Observed CPU | Observed memory | Resource request based on the fixture sample |
| --- | ---: | ---: | --- |
| Live API | 286m | 77 MiB | 300m CPU, 128 MiB |
| Candidate API | 274m | 77 MiB | 300m CPU, 128 MiB |
| Chroma | 178m | 87 MiB | 200m CPU, 128 MiB |

This is a fixture-scale sample. Full ingestion and evaluation Job resource sizing and the production release decision still require workload measurements. [Minikube resource output](../eval/results/resources_minikube_fixture.txt)

## Short answers

**(a)** Uniqueness caught both copied documents and the lightly edited duplicate. Completeness caught the missing title and missing page. The locker document passed verification and was flagged as suspicious. A retrieval rail can remove instruction-like chunks before generation. Meaning-changing or indirect instructions can evade pattern matching. [Batch B verification](../eval/results/verification_report_20261123T194050Z-9cf18ab7.json)

**(b)** Use one example from the measured module, ranked retrieval and per-question generation outputs once the three-level runs finish.

**(c)** Archiving preserves the bytes and provenance needed to restore an old version and reproduce a citation. Deleting lake bytes eliminates those recovery options. Removing its derived chunks keeps stale content outside the active index.

**(d)** Faithfulness measures whether the generator quotes the selected evidence. A fully supported quote can still address the wrong policy, which is why correctness and retrieval labels are scored separately.

**(e)** The difficult design trade-off is semantic verification across long documents. Shared report structure can make independently valid reports look redundant. The recorded Batch A false positive is evidence of that limitation. [Full Batch A verification](../eval/results/verification_report_20261123T193246Z-8e991eba.json)

**(f)** The ingestion Job owns writes and the CronJob schedules them. The PVC retains raw and archived data. The Chroma StatefulSet retains the vector state. The ConfigMap supplies gate limits. Services isolate candidate and live traffic. Deployment rolling updates and rollout history handle release and reversal.

## Contributions and AI disclosure

| Member | Work or review |
| --- | --- |
| Member 1 | [Confirm implemented, reviewed and demonstrated tasks] |
| Member 2 | [Confirm implemented, reviewed and demonstrated tasks] |

Codex assisted with implementation, original synthetic fixtures, documentation and execution. The project owner wrote the eight questions identified as human-authored. The team will record its contributions, review synthetic labels and demonstrate the Kubernetes flow.
