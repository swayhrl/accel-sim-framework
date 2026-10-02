#!/usr/bin/env python3
"""One-process R23G B0 qualification and live RULE_U01 validation campaign."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jsonschema
import numpy as np
import torch
import xgrammar as xgr
from safetensors import safe_open
from transformers import AutoModelForCausalLM, AutoTokenizer


VOCAB = 151936
MASK_WORDS = VOCAB // 32
A0 = "A0_DENSE_VENDOR"
A3 = "A3_RAGGED_DIRECT"
B0 = "B0_STRONG"
M1 = "M1_RULE_U01"
MAX_NEW_TOKENS = 128


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def median(values):
    return statistics.median(values)


def mad(values):
    med = median(values)
    return median([abs(value - med) for value in values])


def unpack_mask(bitmask: torch.Tensor, vocab_size: int) -> np.ndarray:
    words = bitmask.numpy().view(np.uint32)
    bits = np.unpackbits(words.view(np.uint8), axis=-1, bitorder="little")
    return bits[..., :vocab_size].astype(bool, copy=False)


@torch.inference_mode()
def fill_masks(matchers, done, mask):
    mask.zero_()
    start = time.perf_counter_ns()
    for i, matcher in enumerate(matchers):
        if not done[i]:
            matcher.fill_next_token_bitmask(mask, i)
    grammar_ms = (time.perf_counter_ns() - start) / 1e6
    legal = unpack_mask(mask, VOCAB)
    active = [i for i in range(4) if not done[i]]
    legal_ids = [
        np.flatnonzero(legal[i]).astype(np.int32, copy=False) for i in range(4)
    ]
    if any(len(legal_ids[i]) == 0 for i in active):
        raise RuntimeError(f"EMPTY_LEGAL_SUPPORT active={active}")
    return legal_ids, grammar_ms


class UnionDispatcher:
    def __init__(self):
        self.union = np.empty(MASK_WORDS, dtype=np.uint32)
        self.lut = np.array([int(i).bit_count() for i in range(256)], dtype=np.uint8)

    def classify(self, mask: torch.Tensor, active: list[int]) -> dict:
        if not active:
            raise ValueError("no active rows for dispatch")
        start_total = time.perf_counter_ns()
        active_words = mask.numpy().view(np.uint32)[active]
        start = time.perf_counter_ns()
        np.bitwise_or.reduce(active_words, axis=0, out=self.union)
        or_ns = time.perf_counter_ns() - start
        start = time.perf_counter_ns()
        union_count = int(self.lut[self.union.view(np.uint8)].sum(dtype=np.uint64))
        popcount_ns = time.perf_counter_ns() - start
        start = time.perf_counter_ns()
        fraction = union_count / VOCAB
        arm = A3 if fraction < 0.01 else A0
        branch_ns = time.perf_counter_ns() - start
        total_ns = time.perf_counter_ns() - start_total
        return {
            "union_count": union_count,
            "union_fraction": fraction,
            "selected_head_arm": arm,
            "union_or_ms": or_ns / 1e6,
            "popcount_ms": popcount_ns / 1e6,
            "branch_ms": branch_ns / 1e6,
            "union_dispatch_total_ms": total_ns / 1e6,
        }


def batch_inputs(records, tokenizer, device):
    encoded = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": record["prompt"]}],
            add_generation_prompt=True,
            tokenize=True,
        )
        for record in records
    ]
    if any(not isinstance(ids, list) or not ids for ids in encoded):
        raise ValueError("chat template failed")
    length = max(map(len, encoded))
    input_ids = []
    attention = []
    for ids in encoded:
        pad = length - len(ids)
        input_ids.append([tokenizer.pad_token_id] * pad + ids)
        attention.append([0] * pad + [1] * len(ids))
    return (
        torch.tensor(input_ids, dtype=torch.long, device=device),
        torch.tensor(attention, dtype=torch.long, device=device),
        encoded,
    )


def result_status(record, tokenizer, token_ids, stop_reason, matcher_terminated):
    text = tokenizer.decode(token_ids, skip_special_tokens=True)
    parsed = None
    parse_ok = False
    schema_valid = False
    error = None
    try:
        parsed = json.loads(text)
        parse_ok = True
        jsonschema.validate(instance=parsed, schema=record["schema"])
        schema_valid = True
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    truncated = stop_reason == "MAX_128_TRUNCATED"
    qualified = parse_ok and schema_valid and not truncated and matcher_terminated
    return {
        "qualified": qualified,
        "generated_text": text,
        "parse_ok": parse_ok,
        "schema_valid": schema_valid,
        "matcher_terminated": matcher_terminated,
        "truncated": truncated,
        "error": error,
    }


def longest_runs(arms: list[str]) -> tuple[int, int, int]:
    if not arms:
        return 0, 0, 0
    transitions = sum(a != b for a, b in zip(arms, arms[1:]))
    best = {A0: 0, A3: 0}
    current = arms[0]
    length = 1
    for arm in arms[1:]:
        if arm == current:
            length += 1
        else:
            best[current] = max(best[current], length)
            current = arm
            length = 1
    best[current] = max(best[current], length)
    return transitions, best[A0], best[A3]


class Campaign:
    def __init__(self, args):
        if os.environ.get("R23_GPU_LOCK_HELD") != "1":
            raise RuntimeError("R23_GPU_LOCK_HELD=1 is required")
        source = Path(args.r81_source)
        sys.path.insert(0, str(source))
        from heads import HeadArms

        self.HeadArms = HeadArms
        self.args = args
        self.root = Path(args.root)
        self.raw = self.root / "raw"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.pool = json.loads(Path(args.pool).read_text())
        self.records = self.pool["records"]
        if len(self.records) != 24:
            raise ValueError("qualification pool is not 24")
        self.tokenizer = AutoTokenizer.from_pretrained(
            args.model, local_files_only=True, padding_side="left"
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
        ).eval().to("cuda:0")
        if self.model.get_output_embeddings().weight.data_ptr() != self.model.model.embed_tokens.weight.data_ptr():
            raise ValueError("head is not tied")
        self.head = self.HeadArms(self.model.get_output_embeddings().weight)
        tokenizer_info = xgr.TokenizerInfo.deserialize_json(Path(args.tokenizer_info).read_text())
        self.compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=4, cache_enabled=True)
        self.compiled = {}
        for record in self.records:
            sid = record["schema_sha256"]
            if sid not in self.compiled:
                self.compiled[sid] = self.compiler.compile_json_schema(
                    record["schema"], strict_mode=True, any_whitespace=True
                )
        self.dispatcher = UnionDispatcher()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.pid = os.getpid()

    def matchers(self, records):
        return [xgr.GrammarMatcher(self.compiled[record["schema_sha256"]]) for record in records]

    @torch.inference_mode()
    def generate(self, records, arm, purpose, capture_steps=True):
        if len(records) != 4:
            raise ValueError("fixed B4 only")
        matchers = self.matchers(records)
        input_ids, attention_mask, prompt_ids = batch_inputs(
            records, self.tokenizer, "cuda:0"
        )
        done = [False] * 4
        stop = [None] * 4
        generated = [[] for _ in range(4)]
        completion_ms = [None] * 4
        cache = None
        grammar_ms_total = 0.0
        live_head_ms = 0.0
        union_or_ms = 0.0
        popcount_ms = 0.0
        branch_ms = 0.0
        union_total_ms = 0.0
        traces = []
        selected_arms = []
        wall_start = time.perf_counter_ns()
        for step in range(MAX_NEW_TOKENS):
            mask = torch.empty((4, MASK_WORDS), dtype=torch.int32)
            future = self.executor.submit(fill_masks, matchers, list(done), mask)
            out = self.model.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                past_key_values=cache,
                use_cache=True,
                return_dict=True,
            )
            cache = out.past_key_values
            hidden = out.last_hidden_state[:, -1, :].contiguous()
            _, grammar_ms = future.result()
            grammar_ms_total += grammar_ms
            active = [i for i in range(4) if not done[i]]

            head_start = time.perf_counter_ns()
            if arm == B0:
                dispatch = {
                    "union_count": "",
                    "union_fraction": "",
                    "selected_head_arm": A0,
                    "union_or_ms": 0.0,
                    "popcount_ms": 0.0,
                    "branch_ms": 0.0,
                    "union_dispatch_total_ms": 0.0,
                }
            elif arm == M1:
                dispatch = self.dispatcher.classify(mask, active)
            else:
                raise ValueError(arm)
            chosen, scores, metadata = self.head.select(
                dispatch["selected_head_arm"], hidden, mask, done
            )
            torch.cuda.synchronize()
            elapsed_head_ms = (time.perf_counter_ns() - head_start) / 1e6
            live_head_ms += elapsed_head_ms
            union_or_ms += dispatch["union_or_ms"]
            popcount_ms += dispatch["popcount_ms"]
            branch_ms += dispatch["branch_ms"]
            union_total_ms += dispatch["union_dispatch_total_ms"]
            selected_arms.append(dispatch["selected_head_arm"])

            next_ids = []
            next_attention = []
            for i in range(4):
                if done[i]:
                    next_ids.append(self.tokenizer.pad_token_id)
                    next_attention.append(0)
                    continue
                token = chosen[i]
                if token is None:
                    raise RuntimeError(f"active row without token {i}/{step}")
                if not matchers[i].accept_token(token):
                    raise RuntimeError(f"matcher rejected {i}/{step}/{token}")
                generated[i].append(token)
                terminated = matchers[i].is_terminated()
                eos = token == self.tokenizer.eos_token_id
                if eos or terminated:
                    done[i] = True
                    stop[i] = "EOS" if eos else "GRAMMAR_TERMINATED"
                    completion_ms[i] = (time.perf_counter_ns() - wall_start) / 1e6
                next_ids.append(token if not done[i] else self.tokenizer.pad_token_id)
                next_attention.append(0 if done[i] else 1)
            if capture_steps:
                traces.append(
                    {
                        "purpose": purpose,
                        "generation_arm": arm,
                        "step": step,
                        "active_rows": len(active),
                        "selected_head_arm": dispatch["selected_head_arm"],
                        "union_count": dispatch["union_count"],
                        "union_fraction": dispatch["union_fraction"],
                        "union_or_ms": dispatch["union_or_ms"],
                        "popcount_ms": dispatch["popcount_ms"],
                        "branch_ms": dispatch["branch_ms"],
                        "union_dispatch_total_ms": dispatch["union_dispatch_total_ms"],
                        "live_head_step_ms": elapsed_head_ms,
                        "head_rows": metadata["head_rows"],
                        "singleton_rows": metadata["singleton_rows"],
                        "group_count": metadata["group_count"],
                        "a3_metadata_cpu_ms": metadata["metadata_cpu_ms"],
                        "selected_token_ids": json.dumps(chosen, separators=(",", ":")),
                    }
                )
            if all(done):
                break
            input_ids = torch.tensor(
                next_ids, dtype=torch.long, device="cuda:0"
            ).view(4, 1)
            attention_mask = torch.cat(
                [
                    attention_mask,
                    torch.tensor(
                        next_attention, dtype=torch.long, device="cuda:0"
                    ).view(4, 1),
                ],
                dim=1,
            )
        torch.cuda.synchronize()
        wall_ms = (time.perf_counter_ns() - wall_start) / 1e6
        for i in range(4):
            if not done[i]:
                stop[i] = "MAX_128_TRUNCATED"
                completion_ms[i] = wall_ms
        statuses = [
            result_status(
                records[i],
                self.tokenizer,
                generated[i],
                stop[i],
                matchers[i].is_terminated(),
            )
            for i in range(4)
        ]
        transitions, longest_a0, longest_a3 = longest_runs(selected_arms)
        return {
            "arm": arm,
            "purpose": purpose,
            "wall_ms": wall_ms,
            "live_head_ms": live_head_ms,
            "grammar_fill_ms_sum_diagnostic": grammar_ms_total,
            "union_or_ms": union_or_ms,
            "popcount_ms": popcount_ms,
            "branch_ms": branch_ms,
            "union_dispatch_total_ms": union_total_ms,
            "A0_steps": sum(x == A0 for x in selected_arms),
            "A3_steps": sum(x == A3 for x in selected_arms),
            "arm_transitions": transitions,
            "longest_A0_run": longest_a0,
            "longest_A3_run": longest_a3,
            "steps": len(selected_arms),
            "prompt_token_counts": [len(ids) for ids in prompt_ids],
            "generated_token_ids": generated,
            "generated_token_sha256": [sha_bytes(canonical(ids)) for ids in generated],
            "stop_reasons": stop,
            "request_completion_ms": completion_ms,
            "statuses": statuses,
            "traces": traces,
        }

    def qualify_pool(self):
        rows = []
        outputs = []
        for offset in range(0, 24, 4):
            batch = self.records[offset : offset + 4]
            result = self.generate(batch, B0, f"QUALIFICATION_{offset//4}", False)
            for local, record in enumerate(batch):
                status = result["statuses"][local]
                rows.append(
                    {
                        "pool_rank": offset + local,
                        "record_sha256": record["record_sha256"],
                        "qualified": status["qualified"],
                        "generated_count": len(result["generated_token_ids"][local]),
                        "stop_reason": result["stop_reasons"][local],
                        "parse_ok": status["parse_ok"],
                        "schema_valid": status["schema_valid"],
                        "matcher_terminated": status["matcher_terminated"],
                        "truncated": status["truncated"],
                        "generated_token_sha256": result["generated_token_sha256"][local],
                        "first_error": status["error"] or "",
                    }
                )
                outputs.append(
                    {
                        "pool_rank": offset + local,
                        "record_sha256": record["record_sha256"],
                        "generated_token_ids": result["generated_token_ids"][local],
                        "generated_text": status["generated_text"],
                        "status": status,
                    }
                )
        write_tsv(self.raw / "QUALIFICATION_RESULTS.tsv", rows)
        (self.raw / "QUALIFICATION_OUTPUTS.json").write_text(
            json.dumps(outputs, indent=2, sort_keys=True) + "\n"
        )
        selected_hashes = [row["record_sha256"] for row in rows if row["qualified"]][:12]
        if len(selected_hashes) < 12:
            raise RuntimeError(f"only {len(selected_hashes)} B0-qualified records")
        lookup = {row["record_sha256"]: row for row in self.records}
        selected = [lookup[value] for value in selected_hashes]
        if selected_hashes != sorted(selected_hashes):
            raise ValueError("final 12 not in canonical hash order")
        frozen = {
            "stage": "AWMA_R23G_R81_LIVE_DISPATCH_109_V1",
            "selection": "first 12 B0-qualified records from hash-sorted 24-row pool",
            "record_hashes": selected_hashes,
            "records": selected,
        }
        frozen_path = self.raw / "FROZEN_VALIDATION_RECORDS.json"
        frozen_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
        cohort_rows = []
        for rank, record in enumerate(selected):
            cohort_rows.append(
                {
                    "validation_rank": rank,
                    "batch": f"V{rank//4}",
                    "batch_row": rank % 4,
                    "record_sha256": record["record_sha256"],
                    "original_row_index": record["original_row_index"],
                    "schema_sha256": record["schema_sha256"],
                    "prompt_sha256": record["prompt_sha256"],
                    "function_name": record["function_name"],
                }
            )
        write_tsv(self.raw / "VALIDATION_COHORT.tsv", cohort_rows)
        preauth = json.loads(
            (Path(self.args.pool).parent / "PUBLIC_INPUT_PREQUAL_AUTHORITY.json").read_text()
        )
        preauth.update(
            {
                "qualification_results_sha256": sha_file(self.raw / "QUALIFICATION_RESULTS.tsv"),
                "qualification_outputs_sha256": sha_file(self.raw / "QUALIFICATION_OUTPUTS.json"),
                "final_12_count": 12,
                "final_12_record_hashes": selected_hashes,
                "frozen_validation_records_sha256": sha_file(frozen_path),
                "validation_cohort_sha256": sha_file(self.raw / "VALIDATION_COHORT.tsv"),
                "qualification_arm": B0,
                "candidate_executed_before_freeze": False,
            }
        )
        (self.raw / "PUBLIC_INPUT_AUTHORITY.json").write_text(
            json.dumps(preauth, indent=2, sort_keys=True) + "\n"
        )
        return selected

    @torch.inference_mode()
    def old_fixture_canary(self):
        cohort = "C1_HETEROGENEOUS_DISCOVERY"
        base = Path(self.args.r81_root) / "raw" / "reference" / cohort
        hidden = torch.load(base / "hidden_bf16.pt", weights_only=True, map_location="cpu").to("cuda:0")
        masks = torch.load(base / "token_bitmask_int32.pt", weights_only=True, map_location="cpu")
        ledger = json.loads((base / "STEP_LEDGER.json").read_text())
        fixture = json.loads((Path(self.args.r81_root) / "raw" / "fixture" / "requests.json").read_text())
        request_ids = [row["request_id"] for row in fixture if row["cohort"] == cohort]
        rows = []
        for step, entry in enumerate(ledger):
            active_ids = set(entry["active_request_ids"])
            done = [request_id not in active_ids for request_id in request_ids]
            active = [i for i in range(4) if not done[i]]
            dispatch = self.dispatcher.classify(masks[step], active)
            expected_count = int(entry["legal_union_count"])
            expected_arm = A3 if expected_count / VOCAB < 0.01 else A0
            chosen, _, _ = self.head.select(expected_arm, hidden[step], masks[step], done)
            torch.cuda.synchronize()
            exact = all(
                done[i] or chosen[i] == entry["selected_token_ids"][i]
                for i in range(4)
            )
            rows.append(
                {
                    "cohort": cohort,
                    "step": step,
                    "online_union_count": dispatch["union_count"],
                    "ledger_union_count": expected_count,
                    "count_exact": dispatch["union_count"] == expected_count,
                    "online_arm": dispatch["selected_head_arm"],
                    "retrospective_arm": expected_arm,
                    "arm_exact": dispatch["selected_head_arm"] == expected_arm,
                    "selected_tokens_exact": exact,
                }
            )
        write_tsv(self.raw / "CANARY_UNION_VALIDATION.tsv", rows)
        if not all(
            row["count_exact"] and row["arm_exact"] and row["selected_tokens_exact"]
            for row in rows
        ):
            raise RuntimeError("old R81 union canary failed")

    def compare_semantics(self, batch, b0_result, m1_result):
        mismatch = None
        if b0_result["generated_token_ids"] != m1_result["generated_token_ids"]:
            for row, (left, right) in enumerate(
                zip(b0_result["generated_token_ids"], m1_result["generated_token_ids"])
            ):
                if left != right:
                    step = next(
                        (i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]),
                        min(len(left), len(right)),
                    )
                    mismatch = {
                        "record_sha256": batch[row]["record_sha256"],
                        "row": row,
                        "step": step,
                        "B0_token": left[step] if step < len(left) else None,
                        "M1_token": right[step] if step < len(right) else None,
                    }
                    break
        exact = (
            mismatch is None
            and b0_result["stop_reasons"] == m1_result["stop_reasons"]
            and all(status["qualified"] for status in b0_result["statuses"])
            and all(status["qualified"] for status in m1_result["statuses"])
        )
        return exact, mismatch

    def semantic_qualification(self, selected):
        rows = []
        reference = {}
        semantic_traces = []
        first_mismatch = None
        for batch_id in range(3):
            name = f"V{batch_id}"
            batch = selected[batch_id * 4 : batch_id * 4 + 4]
            b0 = self.generate(batch, B0, f"SEMANTIC_{name}_B0")
            m1 = self.generate(batch, M1, f"SEMANTIC_{name}_M1")
            exact, mismatch = self.compare_semantics(batch, b0, m1)
            if mismatch is not None and first_mismatch is None:
                first_mismatch = {"batch": name, **mismatch}
            reference[name] = b0["generated_token_ids"]
            semantic_traces.extend({"batch": name, **row} for row in m1["traces"])
            rows.append(
                {
                    "batch": name,
                    "selected_tokens_exact": exact,
                    "stop_positions_exact": b0["stop_reasons"] == m1["stop_reasons"],
                    "all_B0_schema_valid": all(x["qualified"] for x in b0["statuses"]),
                    "all_M1_schema_valid": all(x["qualified"] for x in m1["statuses"]),
                    "no_truncation": all(x != "MAX_128_TRUNCATED" for x in b0["stop_reasons"] + m1["stop_reasons"]),
                    "matcher_clean_termination": all(x["matcher_terminated"] for x in b0["statuses"] + m1["statuses"]),
                    "steps": m1["steps"],
                    "A0_steps": m1["A0_steps"],
                    "A3_steps": m1["A3_steps"],
                    "arm_transitions": m1["arm_transitions"],
                    "longest_A0_run": m1["longest_A0_run"],
                    "longest_A3_run": m1["longest_A3_run"],
                    "first_mismatch": json.dumps(mismatch, separators=(",", ":")) if mismatch else "",
                }
            )
        write_tsv(self.raw / "SEMANTIC_QUALIFICATION.tsv", rows)
        write_tsv(self.raw / "SEMANTIC_PER_STEP_DISPATCH_TRACE.tsv", semantic_traces)
        (self.raw / "FIRST_MISMATCH.json").write_text(
            json.dumps(
                {"status": "NONE" if first_mismatch is None else "MISMATCH", "first_mismatch": first_mismatch},
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        if not all(row["selected_tokens_exact"] for row in rows):
            raise RuntimeError("mixed dispatch semantics failed")
        return reference, rows

    def formal(self, selected, reference):
        timing = []
        traces = []
        raw_path = self.raw / "FORMAL_RUNS.jsonl"
        raw_path.write_text("")
        for batch_id in range(3):
            batch_name = f"V{batch_id}"
            batch = selected[batch_id * 4 : batch_id * 4 + 4]
            for group in range(3):
                order = [B0, M1] if group % 2 == 0 else [M1, B0]
                for arm in order:
                    for warmup in range(2):
                        result = self.generate(
                            batch, arm, f"WARMUP_{batch_name}_G{group}_{arm}_{warmup}", False
                        )
                        if result["generated_token_ids"] != reference[batch_name]:
                            raise RuntimeError("warmup semantic mismatch")
                for pair_rep in range(5):
                    for order_index, arm in enumerate(order):
                        purpose = f"FORMAL_{batch_name}_G{group}_P{pair_rep}_{arm}"
                        result = self.generate(batch, arm, purpose, True)
                        if result["generated_token_ids"] != reference[batch_name]:
                            raise RuntimeError("formal semantic mismatch")
                        if not all(x["qualified"] for x in result["statuses"]):
                            raise RuntimeError("formal schema/termination mismatch")
                        row = {
                            "batch": batch_name,
                            "group": group,
                            "pair_rep": pair_rep,
                            "order_index": order_index,
                            "arm": arm,
                            "complete_generation_ms": result["wall_ms"],
                            "live_head_ms": result["live_head_ms"],
                            "union_or_ms": result["union_or_ms"],
                            "popcount_ms": result["popcount_ms"],
                            "branch_ms": result["branch_ms"],
                            "union_dispatch_total_ms": result["union_dispatch_total_ms"],
                            "steps": result["steps"],
                            "A0_steps": result["A0_steps"],
                            "A3_steps": result["A3_steps"],
                            "arm_transitions": result["arm_transitions"],
                            "longest_A0_run": result["longest_A0_run"],
                            "longest_A3_run": result["longest_A3_run"],
                            "semantic_exact": True,
                            "schema_valid": True,
                        }
                        timing.append(row)
                        traces.extend(
                            {
                                "batch": batch_name,
                                "group": group,
                                "pair_rep": pair_rep,
                                **trace,
                            }
                            for trace in result["traces"]
                        )
                        with raw_path.open("a") as f:
                            f.write(
                                json.dumps(
                                    {
                                        **row,
                                        "record_hashes": [x["record_sha256"] for x in batch],
                                        "generated_token_ids": result["generated_token_ids"],
                                        "generated_token_sha256": result["generated_token_sha256"],
                                        "stop_reasons": result["stop_reasons"],
                                        "statuses": result["statuses"],
                                    },
                                    sort_keys=True,
                                )
                                + "\n"
                            )
        live_rows = [
            {
                "batch": row["batch"],
                "group": row["group"],
                "pair_rep": row["pair_rep"],
                "order_index": row["order_index"],
                "arm": row["arm"],
                "live_head_ms": f"{row['live_head_ms']:.9f}",
                "union_dispatch_total_ms": f"{row['union_dispatch_total_ms']:.9f}",
                "steps": row["steps"],
                "A0_steps": row["A0_steps"],
                "A3_steps": row["A3_steps"],
                "arm_transitions": row["arm_transitions"],
                "semantic_exact": row["semantic_exact"],
            }
            for row in timing
        ]
        complete_rows = [
            {
                "batch": row["batch"],
                "group": row["group"],
                "pair_rep": row["pair_rep"],
                "order_index": row["order_index"],
                "arm": row["arm"],
                "complete_generation_ms": f"{row['complete_generation_ms']:.9f}",
                "steps": row["steps"],
                "semantic_exact": row["semantic_exact"],
                "schema_valid": row["schema_valid"],
            }
            for row in timing
        ]
        write_tsv(self.raw / "FORMAL_LIVE_HEAD_TIMING.tsv", live_rows)
        write_tsv(self.raw / "FORMAL_COMPLETE_GENERATION_TIMING.tsv", complete_rows)
        write_tsv(self.raw / "PER_STEP_DISPATCH_TRACE.tsv", traces)
        return timing, traces

    def summarize(self, timing, traces, semantic_rows):
        group_rows = []
        batch_rows = []
        stable_positive_batches = 0
        stable_regression_batches = 0
        complete_regression_batches = 0
        for batch in ["V0", "V1", "V2"]:
            group_positive = []
            group_regression = []
            complete_regression = []
            for group in range(3):
                by_arm = {
                    arm: [
                        row
                        for row in timing
                        if row["batch"] == batch and row["group"] == group and row["arm"] == arm
                    ]
                    for arm in (B0, M1)
                }
                b0_live = [row["live_head_ms"] for row in by_arm[B0]]
                m1_live = [row["live_head_ms"] for row in by_arm[M1]]
                b0_complete = [row["complete_generation_ms"] for row in by_arm[B0]]
                m1_complete = [row["complete_generation_ms"] for row in by_arm[M1]]
                live_gap = median(b0_live) - median(m1_live)
                live_noise = 3 * max(mad(b0_live), mad(m1_live))
                complete_gap = median(m1_complete) - median(b0_complete)
                complete_noise = 3 * max(mad(b0_complete), mad(m1_complete))
                positive = live_gap > 0 and live_gap > live_noise
                regression = live_gap < 0 and -live_gap > live_noise
                complete_reg = (
                    median(m1_complete) / median(b0_complete) > 1.02
                    and complete_gap > complete_noise
                )
                group_positive.append(positive)
                group_regression.append(regression)
                complete_regression.append(complete_reg)
                group_rows.append(
                    {
                        "batch": batch,
                        "group": group,
                        "B0_live_median_ms": median(b0_live),
                        "M1_live_median_ms": median(m1_live),
                        "live_gap_B0_minus_M1_ms": live_gap,
                        "live_gap_fraction_of_B0": live_gap / median(b0_live),
                        "three_x_larger_live_MAD_ms": live_noise,
                        "stable_local_positive": positive,
                        "stable_local_regression": regression,
                        "B0_complete_median_ms": median(b0_complete),
                        "M1_complete_median_ms": median(m1_complete),
                        "complete_M1_vs_B0_fraction": median(m1_complete) / median(b0_complete) - 1,
                        "three_x_larger_complete_MAD_ms": complete_noise,
                        "stable_complete_regression_gt_2pct": complete_reg,
                    }
                )
            batch_positive = all(group_positive)
            batch_regression = all(group_regression)
            batch_complete_regression = all(complete_regression)
            stable_positive_batches += batch_positive
            stable_regression_batches += batch_regression
            complete_regression_batches += batch_complete_regression
            semantic = next(row for row in semantic_rows if row["batch"] == batch)
            batch_rows.append(
                {
                    "batch": batch,
                    "stable_local_positive": batch_positive,
                    "stable_local_regression": batch_regression,
                    "stable_complete_regression_gt_2pct": batch_complete_regression,
                    "semantic_qualified": semantic["selected_tokens_exact"],
                    "steps": semantic["steps"],
                    "A0_steps": semantic["A0_steps"],
                    "A3_steps": semantic["A3_steps"],
                    "arm_transitions": semantic["arm_transitions"],
                    "longest_A0_run": semantic["longest_A0_run"],
                    "longest_A3_run": semantic["longest_A3_run"],
                }
            )
        semantics_ok = all(row["semantic_qualified"] for row in batch_rows)
        if (
            semantics_ok
            and stable_positive_batches >= 2
            and stable_regression_batches == 0
            and complete_regression_batches < 2
        ):
            decision = "R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT"
        elif stable_positive_batches == 0 or stable_regression_batches > 0:
            decision = "R23G_R81_LIVE_DISPATCH_NOT_BENEFICIAL"
        else:
            decision = "R23G_R81_LIVE_DISPATCH_RESULT_MIXED"

        union_rows = []
        for batch in ["V0", "V1", "V2"]:
            m1 = [row for row in timing if row["batch"] == batch and row["arm"] == M1]
            batch_traces = [
                row for row in traces if row["batch"] == batch and row["generation_arm"] == M1
            ]
            union_rows.append(
                {
                    "batch": batch,
                    "formal_generations": len(m1),
                    "median_union_OR_sum_ms": median([x["union_or_ms"] for x in m1]),
                    "median_popcount_sum_ms": median([x["popcount_ms"] for x in m1]),
                    "median_branch_sum_ms": median([x["branch_ms"] for x in m1]),
                    "median_union_dispatch_sum_ms": median([x["union_dispatch_total_ms"] for x in m1]),
                    "median_union_OR_per_step_ms": median([x["union_or_ms"] for x in batch_traces]),
                    "median_popcount_per_step_ms": median([x["popcount_ms"] for x in batch_traces]),
                    "median_branch_per_step_ms": median([x["branch_ms"] for x in batch_traces]),
                    "median_union_dispatch_per_step_ms": median([x["union_dispatch_total_ms"] for x in batch_traces]),
                }
            )
        write_tsv(self.raw / "GROUP_RESPONSE_SUMMARY.tsv", group_rows)
        write_tsv(self.raw / "BATCH_RESPONSE_SUMMARY.tsv", batch_rows)
        write_tsv(self.raw / "UNION_COST_SUMMARY.tsv", union_rows)
        summary = {
            "decision": decision,
            "stable_local_positive_batches": stable_positive_batches,
            "stable_local_regression_batches": stable_regression_batches,
            "stable_complete_regression_batches_gt_2pct": complete_regression_batches,
            "batch_rows": batch_rows,
            "group_rows": group_rows,
            "union_cost_rows": union_rows,
        }
        (self.raw / "RESPONSE_SUMMARY.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        return summary

    def environment_receipt(self):
        receipt = {
            "pid": self.pid,
            "python": sys.version,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "transformers": importlib.metadata.version("transformers"),
            "xgrammar": importlib.metadata.version("xgrammar"),
            "triton": importlib.metadata.version("triton"),
            "numpy": np.__version__,
            "jsonschema": importlib.metadata.version("jsonschema"),
            "gpu": torch.cuda.get_device_name(0),
            "device_capability": list(torch.cuda.get_device_capability(0)),
            "campaign_lock_env": os.environ.get("R23_GPU_LOCK_HELD"),
        }
        (self.raw / "ENVIRONMENT.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )

    def run(self):
        self.environment_receipt()
        selected = self.qualify_pool()
        # The final 12 and hashes are durable before the first M1 execution.
        freeze_receipt = self.raw / "FINAL_12_FROZEN_UTC.txt"
        freeze_receipt.write_text(
            f"FINAL_12_FROZEN_UTC={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        )
        self.old_fixture_canary()
        reference, semantic_rows = self.semantic_qualification(selected)
        timing, traces = self.formal(selected, reference)
        summary = self.summarize(timing, traces, semantic_rows)
        print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer-info", required=True)
    ap.add_argument("--r81-root", required=True)
    ap.add_argument("--r81-source", required=True)
    return ap.parse_args()


if __name__ == "__main__":
    campaign = Campaign(parse_args())
    try:
        campaign.run()
    finally:
        campaign.executor.shutdown(wait=True)
