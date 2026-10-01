#!/usr/bin/env python3
"""Freeze one real HELMET Banking77 prompt from the reproduction harness."""

import argparse
import ast
import csv
import hashlib
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--banking-source", type=Path, required=True)
    ap.add_argument("--dataset-script", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(args.source_root))
    from benchmark.data_gen import helmet_runner

    # The mirror used on node109 does not expose the synthetic
    # refs/convert/parquet ref. The current dataset is already parquet-backed,
    # so fall back to the public main revision while retaining the harness's
    # deterministic sampling and rendering code.
    def mirror_compatible_loader(task: str):
        if task != "helmet_banking77":
            raise KeyError(task)
        dataset_script = args.dataset_script
        tree = ast.parse(dataset_script.read_text())
        names = None
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "names" and isinstance(node.value, ast.List):
                candidate = ast.literal_eval(node.value)
                if len(candidate) == 77:
                    names = candidate
                    break
        if names is None:
            raise RuntimeError("could not recover Banking77 ClassLabel names")
        label_to_id = {name: i for i, name in enumerate(names)}

        def read_rows(path: Path):
            with path.open(newline="", encoding="utf-8") as f:
                return [
                    {"text": row["text"], "label": label_to_id[row["category"]]}
                    for row in csv.DictReader(f)
                ]

        train = read_rows(args.banking_source / "banking_data" / "train.csv")
        test = read_rows(args.banking_source / "banking_data" / "test.csv")
        return train, test, names, "text", "label"

    helmet_runner._load_icl_dataset = mirror_compatible_loader

    row = next(
        helmet_runner._icl_examples(
            task="helmet_banking77",
            target_tokens=8192,
            num_samples=1,
            seed=1337,
        )
    )
    prompt = row["prompt"]
    payload = {
        "authority": "PUBLIC_REPRODUCTION_ARTIFACT",
        "dataset": "PolyAI/banking77",
        "dataset_revision_requested": "refs/convert/parquet",
        "dataset_revision_used": "PolyAI-LDN/task-specific-datasets@57ec275d8078af65b7731c2a98be812d844a6d6b",
        "generator_source": "benchmark/data_gen/helmet_runner.py",
        "task": row["task"],
        "example_id": row["id"],
        "seed": 1337,
        "target_tokens_in_harness": 8192,
        "full_prompt_utf8_bytes": len(prompt.encode("utf-8")),
        "full_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "question": row["question"],
        "answer": row["answer"],
        "metadata": row["metadata"],
        "prompt": prompt,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: payload[k] for k in payload if k != "prompt"}, indent=2))


if __name__ == "__main__":
    main()
