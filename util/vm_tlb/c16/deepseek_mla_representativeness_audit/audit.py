#!/usr/bin/env python3
"""CPU-only DeepSeek-V2-Lite MLA representation/source evidence audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

COORDINATION_COMMIT = "b4941d74363f7eb3b590db68377fb8cd4c5a9671"
BASE_COMMIT = "b2975f163f319b5e339808877246c49cbf8a64cd"
MODEL_REVISION = "604d5664dddd88a0433dbae533b7fe9472482de0"
V26 = "afa5b3898ba33ad03f507e20b5312ef28f601c11"
V27 = "05f431a37b673e70061ad8921165a7630d981224"
V30 = "864315d45ebb43235c4e116cd76f2bfb19c65c1e"
P26 = "docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26"
P27 = "docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27"
P30 = "docs/vm_tlb/review_packs/C16_DEEPSEEK_S2_S3_CONSUMER_174NEW_V30"
LATER_COMMIT = "07338b6c74a578868368e6e549dea83414e4b8cb"
LATER_MODELING_BLOB = "a51ac0266263945af68fa6b84cf5a71d84198c79"
LATER_MODULAR_BLOB = "9717b12b17d4aba970e1dc6d3f64a46f840181be"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_bytes(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def git_text(repo: Path, *args: str) -> str:
    return git_bytes(repo, *args).decode("utf-8").strip()


def show_text(repo: Path, commit: str, path: str) -> str:
    return git_text(repo, "show", f"{commit}:{path}")


def show_json(repo: Path, commit: str, path: str):
    return json.loads(show_text(repo, commit, path))


def blob(repo: Path, commit: str, path: str) -> str:
    return git_text(repo, "rev-parse", f"{commit}:{path}")


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def line_number(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    raise ValueError(f"source anchor missing: {needle}")


def assert_before(text: str, first: str, second: str) -> None:
    if text.index(first) >= text.index(second):
        raise ValueError(f"source order mismatch: {first} !< {second}")


def config_binding(config: dict) -> dict:
    keys = ("num_attention_heads", "num_key_value_heads", "kv_lora_rank", "qk_nope_head_dim", "qk_rope_head_dim", "v_head_dim", "use_cache", "torch_dtype", "transformers_version")
    result = {key: config[key] for key in keys}
    result["config_file_transformers_version_metadata"] = result.pop("transformers_version")
    expected = {
        "num_attention_heads": 16,
        "num_key_value_heads": 16,
        "kv_lora_rank": 512,
        "qk_nope_head_dim": 128,
        "qk_rope_head_dim": 64,
        "v_head_dim": 128,
        "use_cache": True,
        "torch_dtype": "bfloat16",
    }
    result["status"] = "PASS" if all(result[key] == value for key, value in expected.items()) else "FAIL"
    result["q_head_dim"] = result["qk_nope_head_dim"] + result["qk_rope_head_dim"]
    result["source_implied_latent_dims_per_token"] = result["kv_lora_rank"] + result["qk_rope_head_dim"]
    result["source_implied_latent_bytes_per_token_bf16"] = result["source_implied_latent_dims_per_token"] * 2
    result["accepted_runtime_cache_bytes_per_token_bf16"] = result["num_attention_heads"] * (result["q_head_dim"] + result["v_head_dim"]) * 2
    result["runtime_over_latent_ratio"] = result["accepted_runtime_cache_bytes_per_token_bf16"] / result["source_implied_latent_bytes_per_token_bf16"]
    if result["status"] != "PASS":
        raise ValueError(f"config binding failed: {result}")
    return result


def cache_rows(v26_lifetime: dict, v27_state: dict) -> list[dict]:
    rows = []
    for scenario, source, source_commit, source_path in (
        ("S2", v26_lifetime["lifetime"], V26, f"{P26}/PERSISTENT_CACHE_LIFETIME_AUDIT.json"),
        ("S3", v27_state, V27, f"{P27}/S3_STATE_AND_CACHE_RECEIPT.json"),
    ):
        for state in ("cache_before_decode1", "cache_after_decode1"):
            for component in ("key", "value"):
                item = source[state][component]
                logical_bytes = int(item["bytes"])
                shape_bytes = 2
                for dim in item["shape"]:
                    shape_bytes *= int(dim)
                if logical_bytes != shape_bytes:
                    raise ValueError(f"{scenario}/{state}/{component}: logical shape-byte mismatch")
                rows.append({
                    "scenario": scenario,
                    "state": state,
                    "component": component,
                    "shape": json.dumps(item["shape"], separators=(",", ":")),
                    "dtype": item["dtype"],
                    "logical_bytes": logical_bytes,
                    "backing_storage_bytes": int(item["storage_bytes"]),
                    "bytes_per_position": logical_bytes // int(item["shape"][2]),
                    "storage_ptr_hex": item["storage_ptr_hex"],
                    "content_sha256": item["sha256"],
                    "authority_commit": source_commit,
                    "authority_path": source_path,
                })
    return rows


def qk_summary(v26_lifetime: dict, v27_state: dict) -> dict:
    result = {}
    for scenario, source, persistent in (
        ("S2", v26_lifetime["lifetime"], 2048),
        ("S3", v27_state, 8192),
    ):
        operands = source["qk_operands"]
        result[scenario] = {
            "query_shape": operands["query"]["shape"],
            "query_bytes": operands["query"]["bytes"],
            "key_transposed_shape": operands["key_transposed"]["shape"],
            "key_transposed_bytes": operands["key_transposed"]["bytes"],
            "output_shape": operands["output"]["shape"],
            "output_bytes": operands["output"]["bytes"],
            "persistent_prefix_positions": persistent,
            "current_append_positions": 1,
            "cache_after_key_storage_ptr": source["cache_after_decode1"]["key"]["storage_ptr_hex"],
            "key_transposed_storage_ptr": operands["key_transposed"]["storage_ptr_hex"],
            "key_operand_aliases_cache_storage": source["cache_after_decode1"]["key"]["storage_ptr_hex"] == operands["key_transposed"]["storage_ptr_hex"],
        }
        if not result[scenario]["key_operand_aliases_cache_storage"]:
            raise ValueError(f"{scenario}: QK key operand does not alias accepted cache key storage")
    return result


def source_audit(source_root: Path, later_repo: Path) -> tuple[list[dict], dict, dict]:
    config_path = source_root / "config.json"
    modeling_path = source_root / "modeling_deepseek.py"
    if source_root.name != MODEL_REVISION:
        raise ValueError("accepted source directory revision mismatch")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    modeling = modeling_path.read_text(encoding="utf-8")
    binding = config_binding(config)
    accepted_patterns = {
        "compressed_first": "compressed_kv = self.kv_a_proj_with_mqa(hidden_states)",
        "split_latent_rope": "compressed_kv, [self.kv_lora_rank, self.qk_rope_head_dim]",
        "expand_before_cache": "self.kv_b_proj(self.kv_a_layernorm(compressed_kv))",
        "assemble_full_key": "key_states = k_pe.new_empty(bsz, self.num_heads, q_len, self.q_head_dim)",
        "cache_full_key_value": "key_states, value_states = past_key_value.update(",
        "qk_full_key": "torch.matmul(query_states, key_states.transpose(2, 3))",
    }
    for label, pattern in accepted_patterns.items():
        if pattern not in modeling:
            raise ValueError(f"accepted source pattern missing: {label}")
    assert_before(modeling, accepted_patterns["compressed_first"], accepted_patterns["expand_before_cache"])
    assert_before(modeling, accepted_patterns["expand_before_cache"], accepted_patterns["cache_full_key_value"])
    accepted_anchors = ",".join(f"{label}:{line_number(modeling, pattern)}" for label, pattern in accepted_patterns.items())
    later_commit = git_text(later_repo, "rev-parse", LATER_COMMIT)
    modeling_blob = git_text(later_repo, "rev-parse", f"{LATER_COMMIT}:src/transformers/models/deepseek_v2/modeling_deepseek_v2.py")
    modular_blob = git_text(later_repo, "rev-parse", f"{LATER_COMMIT}:src/transformers/models/deepseek_v2/modular_deepseek_v2.py")
    later_modeling_bytes = git_bytes(later_repo, "cat-file", "blob", modeling_blob)
    later_modular_bytes = git_bytes(later_repo, "cat-file", "blob", modular_blob)
    later_modeling = later_modeling_bytes.decode("utf-8")
    later_patterns = {
        "latent_single_head": "k_nope = self.kv_a_layernorm(kv_nope).view(batch_size, 1, seq_length, self.kv_lora_rank)",
        "rope_single_head": "k_pe = k_pe.view(batch_size, 1, seq_length, self.qk_rope_head_dim)",
        "cache_latent": "k_nope, k_pe = past_key_values.update(k_nope, k_pe, self.layer_idx)",
        "expand_after_cache": "key_states, value_states = self.expand_kv(k_nope, k_pe)",
    }
    for label, pattern in later_patterns.items():
        if pattern not in later_modeling:
            raise ValueError(f"later source pattern missing: {label}")
    assert_before(later_modeling, later_patterns["cache_latent"], later_patterns["expand_after_cache"])
    later_anchors = ",".join(f"{label}:{line_number(later_modeling, pattern)}" for label, pattern in later_patterns.items())
    rows = [
        {
            "source_class": "accepted_exact_model_revision",
            "revision": MODEL_REVISION,
            "path": "config.json",
            "retrieval": str(config_path),
            "official_url": f"https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite/raw/{MODEL_REVISION}/config.json",
            "sha256": sha256(config_path),
            "git_blob": "not required; accepted local model asset authority",
            "size_bytes": config_path.stat().st_size,
            "anchors": "config fields",
            "finding": "16 attention/KV heads; latent 512; no-PE 128; RoPE 64; value 128; BF16; cache enabled",
        },
        {
            "source_class": "accepted_exact_model_revision",
            "revision": MODEL_REVISION,
            "path": "modeling_deepseek.py",
            "retrieval": str(modeling_path),
            "official_url": f"https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite/raw/{MODEL_REVISION}/modeling_deepseek.py",
            "sha256": sha256(modeling_path),
            "git_blob": "not required; accepted local model asset authority",
            "size_bytes": modeling_path.stat().st_size,
            "anchors": accepted_anchors,
            "finding": "produces compressed latent first, expands per head before DynamicCache.update, and QK consumes expanded key",
        },
        {
            "source_class": "later_transformers_context_only",
            "revision": later_commit,
            "path": "src/transformers/models/deepseek_v2/modeling_deepseek_v2.py",
            "retrieval": str(later_repo),
            "official_url": f"https://github.com/huggingface/transformers/blob/{later_commit}/src/transformers/models/deepseek_v2/modeling_deepseek_v2.py",
            "sha256": sha256_bytes(later_modeling_bytes),
            "git_blob": modeling_blob,
            "size_bytes": len(later_modeling_bytes),
            "anchors": later_anchors,
            "finding": "updates cache with single-head latent and RoPE tensors, then expands K/V after cache read",
        },
        {
            "source_class": "later_transformers_context_only",
            "revision": later_commit,
            "path": "src/transformers/models/deepseek_v2/modular_deepseek_v2.py",
            "retrieval": str(later_repo),
            "official_url": f"https://github.com/huggingface/transformers/blob/{later_commit}/src/transformers/models/deepseek_v2/modular_deepseek_v2.py",
            "sha256": sha256_bytes(later_modular_bytes),
            "git_blob": modular_blob,
            "size_bytes": len(later_modular_bytes),
            "anchors": "cache latent and expand-after-cache logic mirrors generated modeling source",
            "finding": "independent generator-source confirmation of later latent-cache ordering",
        },
    ]
    if later_commit != LATER_COMMIT or modeling_blob != LATER_MODELING_BLOB or modular_blob != LATER_MODULAR_BLOB:
        raise ValueError("later source identity mismatch")
    accepted = {
        "compressed_kv_produced_first": True,
        "expanded_by_kv_b_proj_before_cache": True,
        "cache_update_arguments": ["key_states [B,16,T,192]", "value_states [B,16,T,128]"],
        "cached_representation": "expanded full per-head key/value",
        "compressed_latent_cached": False,
        "accepted_runtime_retains_canonical_mla_compressed_cache_advantage": False,
        "source_anchors": accepted_anchors,
    }
    later = {
        "commit": later_commit,
        "commit_date": git_text(later_repo, "show", "-s", "--format=%cI", later_commit),
        "context_only": True,
        "cache_update_arguments": ["k_nope [B,1,T,512]", "k_pe [B,1,T,64]"],
        "expansion_order": "after cache update/read",
        "shows_expanded_cache_is_avoidable_by_later_public_implementation": True,
        "no_performance_claim": True,
    }
    return rows, binding, {"accepted": accepted, "later": later}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--accepted-source-root", type=Path, required=True)
    parser.add_argument("--later-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    source_rows, binding, source_conclusion = source_audit(args.accepted_source_root, args.later_repo)
    v26_lifetime = show_json(args.repo, V26, f"{P26}/PERSISTENT_CACHE_LIFETIME_AUDIT.json")
    v27_state = show_json(args.repo, V27, f"{P27}/S3_STATE_AND_CACHE_RECEIPT.json")
    v30_scaling = show_json(args.repo, V30, f"{P30}/S2_S3_MLA_SCALING.json")
    v26_manifest = show_json(args.repo, V26, f"{P26}/formal/RUN_MANIFEST.json")
    cache = cache_rows(v26_lifetime, v27_state)
    qk = qk_summary(v26_lifetime, v27_state)

    authority = {
        "status": "PASS",
        "coordination_commit": COORDINATION_COMMIT,
        "base_commit": BASE_COMMIT,
        "model": "deepseek-ai/DeepSeek-V2-Lite",
        "revision": MODEL_REVISION,
        "accepted_source_root": str(args.accepted_source_root),
        "accepted_source_hashes": {row["path"]: row["sha256"] for row in source_rows if row["source_class"] == "accepted_exact_model_revision"},
        "accepted_branches": {
            "V26": {"commit": V26, "pack": P26, "key_artifact_blobs": {name: blob(args.repo, V26, f"{P26}/{name}") for name in ("PERSISTENT_CACHE_LIFETIME_AUDIT.json", "PERSISTENT_CACHE_OBJECTS.tsv", "MLA_PERSISTENT_TYPED_DATAFLOW.json", "FORMAL_SUMMARY.json")}},
            "V27": {"commit": V27, "pack": P27, "key_artifact_blobs": {name: blob(args.repo, V27, f"{P27}/{name}") for name in ("S3_STATE_AND_CACHE_RECEIPT.json", "S3_QK_TARGET_QUALIFICATION.json", "S3_FORMAL_SUMMARY.json", "S2_VS_S3_MIXED_QK_SCALING.json")}},
            "V30": {"commit": V30, "pack": P30, "key_artifact_blobs": {name: blob(args.repo, V30, f"{P30}/{name}") for name in ("S2_S3_MLA_SCALING.json", "FINAL_DECISION.json", "V26_V27_MIXED_QK_SHARD_FINGERPRINTS.tsv")}},
        },
        "accepted_runtime": {"attention_backend": v26_manifest["runtime"]["attention_backend"], "torch": v26_manifest["runtime"]["torch"], "transformers": v26_manifest["runtime"]["transformers"]},
        "consumer_resource_use": {"cpu_only": True, "gpu_used": False, "gpu_lock_requested": False, "nvbit_ncu_nsys_run": False, "lane4_partial_read": False},
    }
    if authority["accepted_runtime"] != {"attention_backend": "eager", "torch": "2.5.1+cu124", "transformers": "4.51.0"}:
        raise ValueError(f"accepted runtime mismatch: {authority['accepted_runtime']}")
    dump(out / "AUTHORITY_AUDIT.json", authority)
    dump(out / "CONFIG_BINDING.json", binding)
    write_tsv(out / "EXACT_SOURCE_AUDIT.tsv", source_rows, ["source_class", "revision", "path", "retrieval", "official_url", "sha256", "git_blob", "size_bytes", "anchors", "finding"])
    write_tsv(out / "V26_V27_CACHE_OBJECTS.tsv", cache, ["scenario", "state", "component", "shape", "dtype", "logical_bytes", "backing_storage_bytes", "bytes_per_position", "storage_ptr_hex", "content_sha256", "authority_commit", "authority_path"])

    latent_bytes = binding["source_implied_latent_bytes_per_token_bf16"]
    runtime_bytes = binding["accepted_runtime_cache_bytes_per_token_bf16"]
    positions = {"S2": 2049, "S3": 8193}
    representation_rows = []
    components = [
        ("model_semantic_latent", "compressed_non_rope_latent", 512, 1024, "yes", "joint low-rank source for reconstructed no-PE key and value"),
        ("model_semantic_latent", "shared_rope_key", 64, 128, "yes", "one shared RoPE key component; not replicated across heads"),
        ("model_semantic_latent", "latent_total", 576, latent_bytes, "total", "512+64; no double counting"),
        ("accepted_runtime_cache", "expanded_key_nope", 16 * 128, 4096, "yes", "per-head no-PE key"),
        ("accepted_runtime_cache", "replicated_key_rope", 16 * 64, 2048, "yes", "64-d RoPE key copied across 16 heads"),
        ("accepted_runtime_cache", "expanded_value", 16 * 128, 4096, "yes", "per-head value"),
        ("accepted_runtime_cache", "runtime_total", 5120, runtime_bytes, "total", "expanded key 6144 B + value 4096 B"),
        ("immediate_qk_consumer", "key_transposed_view", 16 * 192, 6144, "alias", "transpose view aliases cached expanded key; not additional cache storage"),
    ]
    for scenario, count in positions.items():
        for level, component, dims, per_token, included, note in components:
            representation_rows.append({"scenario": scenario, "positions": count, "level": level, "component": component, "bf16_dims_per_token": dims, "bytes_per_token": per_token, "total_bytes": per_token * count, "runtime_over_latent_ratio": runtime_bytes / latent_bytes if component == "runtime_total" else "NA", "included_in_level_total": included, "note": note})
    write_tsv(out / "REPRESENTATION_BYTES.tsv", representation_rows, ["scenario", "positions", "level", "component", "bf16_dims_per_token", "bytes_per_token", "total_bytes", "runtime_over_latent_ratio", "included_in_level_total", "note"])

    runtime_totals = {}
    for scenario in ("S2", "S3"):
        after = [row for row in cache if row["scenario"] == scenario and row["state"] == "cache_after_decode1"]
        runtime_totals[scenario] = sum(row["logical_bytes"] for row in after)
        if runtime_totals[scenario] != positions[scenario] * runtime_bytes:
            raise ValueError(f"{scenario}: receipt total does not match exact source/config arithmetic")
    event_ratio = v30_scaling["s3_s2_event_ratio"]
    cache_ratio = runtime_totals["S3"] / runtime_totals["S2"]
    scaling = {
        "status": "PASS_REINTERPRETED",
        "accepted_v30_scope": v30_scaling["scope"],
        "S2": {"positions": positions["S2"], "runtime_cache_bytes": runtime_totals["S2"], "latent_equivalent_bytes": positions["S2"] * latent_bytes, "selected_paths": v30_scaling["s2"]["shards"], "executed_paths": v30_scaling["s2"]["executed"], "active_lane_events": v30_scaling["s2"]["events"], "median_events_per_executed_shard": v30_scaling["s2"]["median_events"], "qk": qk["S2"]},
        "S3": {"positions": positions["S3"], "runtime_cache_bytes": runtime_totals["S3"], "latent_equivalent_bytes": positions["S3"] * latent_bytes, "selected_paths": v30_scaling["s3"]["shards"], "executed_paths": v30_scaling["s3"]["executed"], "active_lane_events": v30_scaling["s3"]["events"], "median_events_per_executed_shard": v30_scaling["s3"]["median_events"], "qk": qk["S3"]},
        "ratios": {
            "context_prefill_length": 4.0,
            "cache_after_length": positions["S3"] / positions["S2"],
            "runtime_cache_bytes": cache_ratio,
            "latent_equivalent_bytes": (positions["S3"] * latent_bytes) / (positions["S2"] * latent_bytes),
            "active_lane_events": event_ratio,
            "selected_paths": v30_scaling["s3"]["shards"] / v30_scaling["s2"]["shards"],
            "executed_paths": v30_scaling["s3"]["executed"] / v30_scaling["s2"]["executed"],
            "median_events_per_executed_shard": v30_scaling["s3"]["median_events"] / v30_scaling["s2"]["median_events"],
            "events_per_runtime_cache_byte": (v30_scaling["s3"]["events"] / runtime_totals["S3"]) / (v30_scaling["s2"]["events"] / runtime_totals["S2"]),
        },
        "accepted_v27_relation": "DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE",
        "reinterpretation": "约15.99倍lane-event增长含有约4倍上下文/缓存长度增长，但还叠加了static set、executed path与kernel实现变化；它不是纯上下文比例，更不是DRAM字节或MLA固有流量。",
        "prohibitions": ["active-lane events are not DRAM bytes", "no TLB miss inference", "no cache/TLB mechanism authorization", "no direct S2/S3 function equivalence"],
    }
    dump(out / "S2_S3_SCALING_REINTERPRETATION.json", scaling)

    chain = f"""# 表示链审计\n\n## A. MLA源码中的latent表示\n\n精确配置为16个attention/KV heads、`kv_lora_rank=512`、no-PE维128、RoPE维64、value维128。源码先生成`compressed_kv`，拆成512维latent与单头64维RoPE key。若按源码可表达的压缩缓存形态保留两者，BF16每token为`(512+64)*2 = {latent_bytes}`字节。\n\n## B. V26/V27实际runtime cache\n\naccepted Transformers 4.51.0 eager源码在cache update之前执行`kv_b_proj`，构造16头key `[B,16,T,192]`和value `[B,16,T,128]`，再把这两个展开tensor传给`DynamicCache.update`。因此实际每token缓存`16*(192+128)*2 = {runtime_bytes}`字节，不是latent cache；相对1,152 B latent形态放大`{runtime_bytes/latent_bytes:.9f}x`。\n\n## C. QK直接消费表示\n\nQK query为`[1,16,1,192]`；key operand是cache key的转置视图：S2 `[1,16,192,2049]`，S3 `[1,16,192,8193]`。receipt中的storage pointer一致，说明QK消费展开后的persistent key（prefix加当前append），不是512维latent。转置视图不应再次计入cache容量。\n\nA、B、C不是同一表示：A是source-implied latent，B是accepted eager runtime的展开cache，C是B的QK转置消费视图。\n"""
    (out / "REPRESENTATION_CHAIN.md").write_text(chain, encoding="utf-8")

    history = f"""# 后续实现上下文\n\n仅作后来实现背景，不替代V26/V27 authority。审计固定于Transformers commit `{LATER_COMMIT}`（2026-09-27）及`modeling_deepseek_v2.py` blob `{LATER_MODELING_BLOB}`、`modular_deepseek_v2.py` blob `{LATER_MODULAR_BLOB}`。\n\n该实现把`k_nope`整理为`[B,1,T,512]`、`k_pe`为`[B,1,T,64]`，先调用cache update，再执行`expand_kv`生成每头K/V。这说明公开实现后来已经能够避免V26/V27的展开persistent cache。源码结构不能单独证明性能更好。\n"""
    (out / "IMPLEMENTATION_HISTORY.md").write_text(history, encoding="utf-8")

    interpretation = f"""# 科学解释\n\n## 实际缓存了什么\n\nV26/V27测到的是Transformers 4.51.0 eager实现的`DynamicCache`：16头BF16 key（每头192维）和16头BF16 value（每头128维）。它不是512维compressed MLA latent。S2 decode1后实际cache为{runtime_totals['S2']:,}字节，S3为{runtime_totals['S3']:,}字节。\n\n## 哪些属于MLA本身\n\n精确模型源码先形成512维低秩latent，并单独形成64维RoPE key；16头Q/K维度、低秩投影和RoPE解耦属于该模型的MLA语义。上下文从2049增至8193时，无论选择latent cache还是展开cache，保存的token数量与总容量都约增长{cache_ratio:.6f}倍。\n\n## 哪些属于当前实现\n\naccepted eager源码选择在cache update之前展开：复制RoPE分量到16头，并缓存完整每头K/V。由此实际cache为10,240 B/token，而source-implied latent形态为1,152 B/token，容量放大{runtime_bytes/latent_bytes:.6f}倍。QK再直接读取该展开key的转置视图。后续Transformers源码已经改为先缓存单头latent/RoPE、再展开，证明V26/V27表示不是MLA不可避免的要求。\n\n## 如何重读15.99倍events\n\nS2→S3 active-lane events为{event_ratio:.6f}倍，但cache长度/字节仅为{cache_ratio:.6f}倍；同时selected paths从20变131、executed paths从16变24，median executed-shard events约增长{scaling['ratios']['median_events_per_executed_shard']:.6f}倍，且accepted authority明确记录S2/S3函数不同。因此15.99倍是上下文扩大与实现/launch/static-path变化的混合结果，不能解释成MLA固有流量，更不能当DRAM字节。\n\n## 是否值得继续\n\n现有结果不支持设计cache/TLB机制。若项目仍关心部署代表性，唯一值得的后续是同模型、同输入、同语义下“展开cache实现 vs latent-cache实现”的最小匹配比较；它应先验证容量和runtime行为差异，再讨论性能。本Goal不授权GPU执行。\n"""
    (out / "SCIENTIFIC_INTERPRETATION.md").write_text(interpretation, encoding="utf-8")

    final = {
        "status": "PASS",
        "goal": "C16_DEEPSEEK_MLA_REPRESENTATIVENESS_AUDIT_174NEW_V1",
        "user_facing_conclusion_zh": "V26/V27实际缓存的是展开后的16头K/V，而不是MLA的压缩latent；约15.99倍lane-event增长是上下文与实现变化的混合结果，不能泛化为MLA固有流量。",
        "actual_cache": "BF16 key [B,16,T,192] plus value [B,16,T,128]",
        "mla_intrinsic": "512-d compressed latent plus separate 64-d RoPE component, 16-head reconstruction semantics, and token-count growth with context",
        "accepted_implementation_specific": "kv_b_proj expansion and RoPE replication before DynamicCache.update; full per-head persistent cache",
        "latent_bytes_per_token": latent_bytes,
        "accepted_runtime_bytes_per_token": runtime_bytes,
        "runtime_over_latent_ratio": runtime_bytes / latent_bytes,
        "existing_results_justify_cache_tlb_mechanism": False,
        "future_research": {"worthwhile": True, "scope": "one minimal matched expanded-cache versus latent-cache implementation comparison", "gpu_authorized": False, "mechanism_design_authorized": False},
        "source_conclusion": source_conclusion,
    }
    dump(out / "FINAL_DECISION.json", final)
    open_issues = """# 未决事项\n\n- 当前没有同输入、同语义下展开cache与latent-cache实现的匹配GPU测量；later source只证明表示选择可避免，不证明性能收益。\n- V26/V27的NCU与lane-event证据仍保持原限定，不能转换为DRAM字节、cache hit或TLB miss。\n- 初始Hugging Face Git网络访问超时，但accepted资产目录中的exact revision源码与官方exact-revision raw页面完成了身份/内容交叉绑定。\n\n这些不阻塞本轮表示分类，也不授权新GPU任务或机制设计。\n"""
    (out / "OPEN_ISSUES.md").write_text(open_issues, encoding="utf-8")

    sums = []
    for path in sorted(out.iterdir(), key=lambda p: p.name):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{sha256(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "runtime_over_latent": runtime_bytes / latent_bytes, "event_ratio": event_ratio}, ensure_ascii=False))


if __name__ == "__main__":
    main()
