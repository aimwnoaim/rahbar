"""Compare measured evaluations and enforce release criteria."""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml


def gate(baseline: Path, candidate: Path, config: Path) -> bool:
    prior = json.loads(baseline.read_text(encoding="utf-8"))
    proposed = json.loads(candidate.read_text(encoding="utf-8"))
    if any(
        prior["environment"][key] != proposed["environment"][key]
        for key in ("seed", "split", "llm_name")
    ):
        raise ValueError("release results must use the same split, seed and generator")
    limits = yaml.safe_load(config.read_text(encoding="utf-8"))
    before, after = prior["mean"], proposed["mean"]
    rules = [
        ("recall_at_5", ">=", max(0, before["recall_at_5"] - limits["recall_at_5_max_drop"])),
        ("faithfulness", ">=", max(0, before["faithfulness"] - limits["faithfulness_max_drop"])),
        ("p95_total_ms", "<=", before["p95_total_ms"] * limits["p95_latency_baseline_factor"]),
        ("abstention_correctness", ">=", before["abstention_correctness"]),
    ]
    print("| Rule | Candidate | Requirement | Result |")
    print("| --- | ---: | ---: | --- |")
    outcomes = []
    for metric, operator, limit in rules:
        value = after.get(metric)
        valid = (
            value is not None and math.isfinite(value) and math.isfinite(limit)
            and (value >= limit if operator == ">=" else value <= limit)
        )
        display = f"{value:.6g}" if value is not None else "missing"
        print(f"| {metric} | {display} | {operator} {limit:.6g} | {'PASS' if valid else 'FAIL'} |")
        outcomes.append(valid)
    print("RELEASE" if all(outcomes) else "REJECT")
    return all(outcomes)
