# Contracts between Member 1 (platform) and Member 2 (data and RAG)

Proposed by Member 1 on 4 Nov 2026. Member 2: reply on PR #1 with "agreed", or quote the exact
line you want changed. A contract changes only by editing this file in a pull request.

## 1. Who owns which files

| Owner | Files |
| --- | --- |
| Member 1 | `api/app/main.py`, `api/app/routes/health.py`, `api/app/routes/metrics.py`, `api/app/logjson.py`, `api/app/config.py` (adds the new fields), `api/app/observability.py` (new), `api/app/services/index_info.py` (new), all Dockerfiles and `.dockerignore`, `k8s/`, `.github/`, `Makefile`, `README.md`, `scripts/`, `docs/adr/0001` and `0004` |
| Member 2 | `api/app/retrieval/chroma.py`, `api/app/providers/llm/*`, `api/app/services/answer.py` and new service modules (cache, validation), `indexer/pipeline/*`, `corpus/`, `eval/`, `docs/CORPUS.md`, `PIPELINE.md`, `FAILURE-ANALYSIS.md`, `docs/adr/0002` and `0003` |
| Shared | `docs/AI-USAGE.md`, `docs/ENGINEERING-NOTES.md`, `api/requirements.txt`, `indexer/requirements.txt` (every new dependency pinned with `==`) |

Branches: Member 1 works on `dev`. Member 2 works on a branch called `rag` and opens pull
requests into `dev`. Member 1 approves them. `dev` goes to `main` by pull request. Nobody pushes to `main`.

## 2. Environment variables (all values live only in the ConfigMap)

| Variable | Read by | Value now | Notes |
| --- | --- | --- | --- |
| `RETRIEVER` | api | `stub` | becomes `chroma` when the real retriever lands |
| `LLM_PROVIDER` | api | `stub` | real provider decided by Friday (see section 7) |
| `LLM_MODEL` | api | `llama3.2:3b` | |
| `EMBED_MODEL` | api, indexer | `dummy-768` | becomes `nomic-embed-text` with the real pipeline |
| `CHROMA_HOST` | api, indexer | `chroma` | the Service name |
| `CHROMA_PORT` | api, indexer | `8000` | |
| `CHROMA_COLLECTION` | api, indexer | `rahbar` | |
| `OLLAMA_URL` | api, indexer | `http://host.minikube.internal:11434` | |
| `HOSTED_BASE_URL` | api | empty | only for hosted mode |
| `TOP_K` | api | `5` | |
| `TEMPERATURE` | api | `0.2` | one-line justification goes next to it in the ConfigMap |
| `RELEVANCE_FLOOR` | api | `0.30` (placeholder) | similarity = 1 - cosine distance. Member 2 tunes it with data |
| `CACHE_THRESHOLD` | api | `0.92` (placeholder) | Member 2 tunes it with data |
| `CACHE_TTL_SECONDS` | api | `604800` | |
| `REDIS_HOST` | api | `redis` | |
| `REDIS_PORT` | api | `6379` | |
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | indexer | `400`, `50` | Member 2 says in PIPELINE.md whether the unit is tokens or characters |
| `CORPUS_DIR` | indexer | `/corpus` | a mounted volume; Member 1 decides how files get there |
| `LOG_LEVEL` | api | `INFO` | |
| `LLM_API_KEY` | api | Secret only | Secret `rahbar-secret`, key `LLM_API_KEY`. Never in the ConfigMap or Git |

Member 1 adds the new fields (`relevance_floor`, `cache_threshold`, `cache_ttl_seconds`,
`redis_host`, `redis_port`) to `api/app/config.py` in the next pull request. Pull `dev` before editing that file.

## 3. Chroma

- Server image `chromadb/chroma:1.0.12`, client `chromadb-client==1.0.12`. Service `chroma`, port 8000.
- One collection, named by `CHROMA_COLLECTION` (`rahbar`), distance `cosine` (`hnsw:space`).
- Collection metadata, written by the indexer, exact keys:
  `embed_model` (string, equal to `EMBED_MODEL`), `dimension` (int, the vector length),
  `index_version` (string, a new unique value on every indexer run, for example `20261106T141500Z`).
- Chunk metadata, exact keys (from `Chunk.metadata()`): `source`, `section`, `page`, `doc_version`, `superseded` (bool).
- Chunk id: stable text, recommended `<source-file-stem>-p<page>-c<n>`.
- The indexer is the only writer. The API only reads.
- Re-index with no downtime (proposal, to be written in ADR 0001): `store()` upserts every chunk
  by its stable id, deletes ids that are no longer in the new set, then updates the collection
  metadata with the new `index_version`. The collection never becomes empty, so `/readyz` stays green.
  If the stored `embed_model` differs from the new one, the collection is deleted and recreated, because the vectors are not comparable.
  Member 2 verifies on the cluster that updating the collection metadata works in Chroma 1.0.12.

## 4. Function signatures where the halves meet

Unchanged from the starter:
- `Retriever.retrieve(question: str, k: int) -> list[Passage]`. Excludes `superseded: true`
  chunks with a metadata filter unless the user explicitly asks about an older version. Returns `[]` when nothing matches.
- `LLMProvider.generate(question: str, passages: list[Passage]) -> Answer`. Providers call
  `record_tokens` themselves inside `generate()` (Ollama reports `prompt_eval_count` and `eval_count`).

Written by Member 2, in `api/app/services/cache.py`:
- `cache_get(question: str) -> AskResponse | None`
- `cache_set(question: str, response: AskResponse) -> None`
- Neither ever raises. A Redis error means a miss, or a no-op for `cache_set`.
- Keys start with `rahbar:cache:<index_version>:` and carry a TTL of `CACHE_TTL_SECONDS`.
- Never cache a follow-up question, an abstention, a fallback, or an answer that failed validation.
- Invalidation on re-index: Redis is reachable from the api only (NetworkPolicy), so the indexer
  cannot flush it. A new `index_version` changes the key prefix, so old entries can no longer be read and then expire by TTL.

Written by Member 1, in `api/app/services/index_info.py`:
- `IndexInfo(embed_model: str, dimension: int, index_version: str, count: int)`
- `get_index_info(settings) -> IndexInfo`, cached for 5 seconds. Raises `IndexUnavailable` when Chroma cannot be reached.

Written by Member 1, in `api/app/observability.py`, called by Member 2 from `answer.py` and the providers:
- `observe_retrieval(seconds: float) -> None`
- `observe_generation(seconds: float) -> None`
- `record_cache(hit: bool) -> None`
- `record_abstention() -> None`
- `record_fallback() -> None`
- `record_tokens(tokens_in: int, tokens_out: int) -> None`
- `log_answered(*, top_k: int, passages: list[Passage], answered_from_context: bool, cached: bool, provider: str) -> None`
  emits the one JSON log line per request. It replaces the `log.info("answered", ...)` call in `answer.py`.

Member 1 pushes `observability.py` and `index_info.py` to `dev` by Friday morning. Until then
Member 2 develops against the stub and keeps the existing log line.

## 5. Images, ports, entry points

| Image | Port | Command |
| --- | --- | --- |
| `rahbar-api` | 8000 | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| `rahbar-indexer` | none | `python -m pipeline.run` (add `--dummy` while using the fake index) |
| `rahbar-ui` | 8080 | nginx with `ui/nginx.conf` |

- Local tag `dev`. In CD the tag is the commit SHA, never `latest`. Docker Hub namespace: to be filled in by Member 1.
- Python 3.12. The indexer image contains `tesseract-ocr` and `poppler-utils` (Member 1 installs them).
- Every container runs as non-root with a read-only root filesystem. Code writes only under `/tmp` (`TMPDIR=/tmp`):
  no model downloads and no caches in the home directory. Test it locally with `docker run --read-only`.
- Network: the indexer talks to Chroma and `OLLAMA_URL` only (plus DNS). The api talks to Chroma, Redis and the LLM host. The indexer cannot reach Redis.

## 6. Evaluation

- CLI (given): `python eval/run_eval.py --api URL [--host rahbar.local] [--golden PATH] [--baseline PATH] [--out PATH] [--update-baseline]`.
  Exit code 0 means the gate passed, 1 means it failed, 2 means not implemented.
- `results.json` keys: `recall_at_3`, `recall_at_5`, `citation_validity`, `abstention_correctness` (all floats from 0 to 1),
  and `recall_at_5_by_type`, an object with one float per question type (`null` if a type has none).
  `main()` adds `golden` and `questions`.
- Gate, implemented by Member 2 in `gate()`: fail if `recall_at_5` is below the baseline value minus 0.05,
  if `abstention_correctness` is below 1.0, or if `citation_validity` is below 0.95. CI reads only the exit code.
- CI runs on the fixture corpus, so it needs its own baseline. Member 2 commits `eval/fixtures/baseline.fixture.json`.
  CI calls `run_eval.py` with `--golden eval/fixtures/golden.fixture.yaml --baseline eval/fixtures/baseline.fixture.json`.
  The real `eval/baseline.json` is for the real corpus only.

## 7. Open questions (to decide by Friday)

1. LLM provider: `ollama-host` or hosted (Groq, Google AI Studio). The laptops have 8 GB of RAM.
   Member 2: can your laptop run `llama3.2:3b` next to minikube? Hosted needs a Secret and affects ADR 0004.
2. CI embeddings: GitHub runners have no model. Member 1's plan is to install Ollama on the runner,
   pull only `nomic-embed-text`, and run CI with `LLM_PROVIDER=stub`. Abstention and citation validity
   must therefore come from the pipeline (the relevance floor and the citation check), not from the model. Member 2: does that work for you?
3. Corpus: which documents did you choose, and how big are they in total? That decides how they reach the Job (volume or image).