# Assignment 03 worklog

## Phase 0 — Checkout and discovery

| Decision or change | Reason and verification |
| --- | --- |
| Reused the existing checkout and pointed `origin` at `aimwnoaim/rahbar`. Created `codex/dev-ragops` at `1e60889`. | The target advertised only `main` at that commit. The existing local `dev` tracked the previous remote. Branch isolation allows Assignment 03 CI to run before any merge. |
| Mapped Parts A–G in [DISCOVERY.md](DISCOVERY.md). | The existing FastAPI, Chroma, Ollama and Redis paths already cover core retrieval and generation. Their current behaviors give the new lifecycle a real baseline. |
| Chose logical document IDs supplied by metadata. | Filenames can change between policy versions. A stable ID links verification, the archive, indexing and traces. |
| Reserved a separate Minikube profile for the clean-cluster demo. | A running `rahbar` profile already hosts earlier work. Docker and Kubernetes tools were confirmed available. |
| Keep evaluation outputs, per-question evidence and traces in version control. | Every report metric must be auditable against a real Assignment 03 run. Workflow checks and historical results remain distinguishable from the new evidence. |
| Use the two requested Git author identities for coherent phases. | The commit attribution is repository metadata. The contribution table will separately record who performed or reviewed the work. |

Discovery commit: `ca354c4`. The running Ollama container has Qwen 2.5 3B and nomic-embed-text. The host Python launcher lists 3.13, so Python 3.11 is still needed for the assignment image. All downloaded corpus originals are present under `corpus/raw/`.

## Phase 1 — Verification and raw-data history

| Decision or change | Reason and verification |
| --- | --- |
| Added separate quality, completeness, recency and uniqueness results. | An operator can see why a revision was quarantined. Exact duplicates use a normalized SHA-256 fingerprint, and a pluggable real embedder supports semantic comparison against active documents. |
| Flagged instruction-like text as informational. | The assignment requires the poisoned document to reach retrieval so the retrieval rail can demonstrate its action. |
| Wrote revision bytes before atomically replacing the manifest. | A crash between these steps leaves raw files available to retry. The manifest records which revision is active and preserves previous bytes for restore. Physical current-directory materialization and index synchronization are still pending. |
| Added verification, duplicate, injection and archive/restore tests. | `python -m pytest tests -q` passed four unit tests. `python -m ruff check ragops tests` passed. The tests use fixed test vectors to isolate the lifecycle and do not produce evaluation evidence. |
| Staged the pinned Assignment 02 originals and added a fictional loan policy to Batch A. | The original corpus exercises extraction. The authored policy gives Batch B a controlled fact change. |
| Added a Chroma reconciliation pass after lake admission. | Exact metadata and ID comparisons detect stale or orphaned chunks. Unchanged chunk hashes avoid embedding work. A fixture rerun embedded zero chunks. |
| Corrected Chroma revision publication after a real run. | The thin client rejects distance metadata in updates. Distance belongs in the creation configuration. |

## Phases 2–6 — Query evidence and offline release checks

| Decision or change | Reason and verification |
| --- | --- |
| Reused the grounded Ollama provider for the RAGOps endpoint. | The trace records both inference calls after the seed is populated. One hash covers both requests. |
| Dropped instruction-like chunks before generation. | Verification flags suspicious text without quarantining it. The trace identifies the dropped chunk and pattern. |
| Used an exact, revision-scoped query cache and bypassed it during evaluation. | Cache hits reuse the original request hashes. Both runs exercise the retrieval and generation stages. |
| Used a quote-overlap faithfulness proxy. | The existing generator produces a source-paired excerpt, so the evaluator can compare it against the actual context. |
| Labeled generated golden questions as pending manual review. | The team can complete human authoring and review using the checklist. The expanded set includes off-topic abstentions. |
| Set the candidate chunk-size limit as the only planned pipeline change. | Both collections can run on one corpus split with the same generator and seed. |
