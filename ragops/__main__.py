"""Command-line entry point for the RAHBAR lifecycle."""

from __future__ import annotations

import argparse
import json
import os
import random
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from uuid import uuid4

import yaml

from indexer.pipeline.config import get_settings
from indexer.pipeline.embed import embed
from indexer.pipeline.store import get_client

from .index import synchronize
from .coverage import coverage
from .evaluation import evaluate
from .ingest import ingest
from .lake import Lake, write_json
from .release import gate
from .tracing import reconstruct, summarize, trace_path


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m ragops")
    parser.add_argument("--data", type=Path, default=Path("/data"))
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("verify", "ingest"):
        command = commands.add_parser(name)
        command.add_argument("--inbox", type=Path, required=True)
        command.add_argument("--out", type=Path, default=Path("eval/results"))
        command.add_argument("--snapshot", action="store_true")
        command.add_argument("--near-threshold", type=float, default=0.95)
        command.add_argument("--min-length", type=int, default=80)
    restore = commands.add_parser("restore")
    restore.add_argument("doc_id")
    restore.add_argument("version")
    commands.add_parser("sync")
    trace = commands.add_parser("trace")
    trace.add_argument("trace_id")
    metrics = commands.add_parser("metrics")
    metrics.add_argument("--since", default="24h")
    evaluate_command = commands.add_parser("eval")
    evaluate_command.add_argument("--collection", required=True)
    evaluate_command.add_argument("--target-url", default=os.getenv("TARGET_URL", "http://localhost:8000"))
    evaluate_command.add_argument("--golden", type=Path, default=Path("eval/golden.jsonl"))
    evaluate_command.add_argument("--pairs", type=Path, default=Path("eval/embedding_pairs.json"))
    evaluate_command.add_argument("--out", type=Path, default=Path("eval/results"))
    evaluate_command.add_argument("--label", default="baseline")
    evaluate_command.add_argument("--split", choices=("a", "ab"), default="a")
    gate_command = commands.add_parser("gate")
    gate_command.add_argument("--baseline", type=Path, required=True)
    gate_command.add_argument("--candidate", type=Path, required=True)
    gate_command.add_argument("--config", type=Path, default=Path("config/gate.yaml"))
    coverage_command = commands.add_parser("coverage")
    coverage_command.add_argument("--live", type=Path, required=True)
    coverage_command.add_argument("--golden", type=Path, required=True)
    coverage_command.add_argument("--threshold", type=float, required=True)
    coverage_command.add_argument("--out", type=Path, default=Path("eval/results"))
    coverage_command.add_argument("--config", type=Path, default=Path("config/gate.yaml"))
    args = parser.parse_args()
    random.seed(0)
    if args.command == "eval":
        print(evaluate(
            args.target_url, args.collection, args.golden, args.pairs, args.out, args.label, args.split,
        ))
        return 0
    if args.command == "gate":
        return 0 if gate(args.baseline, args.candidate, args.config) else 1
    if args.command == "coverage":
        settings = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        result = coverage(args.live, args.golden, args.threshold, args.out)
        return 0 if result["coverage"] >= settings["coverage_minimum"] else 1
    if args.command == "trace":
        print(json.dumps(reconstruct(trace_path(), args.trace_id), ensure_ascii=False, indent=2))
        return 0
    if args.command == "metrics":
        print(json.dumps(summarize(trace_path(), float(args.since.removesuffix("h"))), indent=2))
        return 0
    if os.getenv("RAGOPS_READ_ONLY", "").lower() == "true":
        parser.error("this workload is configured read-only and cannot modify the lake or index")
    lake = Lake(args.data)
    settings = get_settings()
    embed_text = partial(embed, settings=settings)
    counts = {}
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    if args.command in {"verify", "ingest"}:
        if not 0 <= args.near_threshold <= 1 or args.min_length < 1:
            parser.error("near-threshold must be in [0, 1] and min-length must be positive")
        result = ingest(
            lake, args.inbox, args.out, run_id, embed_text, near_threshold=args.near_threshold,
            min_length=args.min_length, snapshot=args.snapshot,
        )
        counts = result["counts"]
    if args.command == "restore":
        lake.restore(args.doc_id, args.version)
    if args.command != "verify":
        if not 0 <= settings.chunk_overlap < settings.chunk_size:
            parser.error("chunk overlap must be nonnegative and smaller than chunk size")
        collection = get_client(settings).get_or_create_collection(
            settings.collection, metadata={
                "embed_model": settings.embed_model,
                "embedding_version": os.getenv("EMBEDDING_VERSION", "unrecorded"),
            },
            configuration={"hnsw": {"space": "cosine"}},
        )
        if collection.metadata.get("embed_model") != settings.embed_model:
            raise ValueError("collection embedding model differs from configuration")
        counts.update(synchronize(
            collection, lake, embed_text, settings.chunk_size, settings.chunk_overlap,
        ))
        metadata = {key: value for key, value in collection.metadata.items() if key != "hnsw:space"}
        collection.modify(metadata=metadata | {"lake_revision": lake.manifest["revision"]})
    if args.command == "ingest":
        write_json(args.out / f"incremental_{run_id}.json", counts)
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
