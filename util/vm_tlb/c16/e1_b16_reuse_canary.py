#!/usr/bin/env python3
"""Deterministic scope/config/analysis tooling for the C16 E1 B16 reuse canary."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


RUN_ID = (
    "C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-"
    "sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03"
)
MANIFEST_SHA = "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389"
CORE_HEAD = "a2322069b9701597db7019080b5b54d29518e3a2"
FRAMEWORK_PARENT = "2fa207fbc37a48f12641d810319b03ba1cf4e381"
PLATFORM_SHA = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
SIDECAR_SHA = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"


class ContractError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tsv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def semantic_range(rows, decode: int, layer: int, identity: str):
    selected = [row for row in rows if int(row["decode_iteration"]) == decode and
                row["semantic_layer"] == str(layer) and
                row["semantic_identity"] == identity and
                row["profile_range_active"] == "True"]
    require(selected, f"missing semantic range {decode}/{layer}/{identity}")
    ids = [int(row["global_dynamic_order"]) for row in selected]
    require(ids == list(range(min(ids), max(ids) + 1)), "semantic range is not contiguous")
    return {"first_dynamic_kernel": min(ids), "last_dynamic_kernel": max(ids),
            "kernel_count": len(ids), "kernel_ids": ids,
            "functions": [row["exact_function"] for row in selected]}


def build_scope(args) -> None:
    require(sha256(args.manifest) == MANIFEST_SHA, "trace manifest SHA drift")
    manifest = read_json(args.manifest)
    require(manifest["run_id"] == RUN_ID and len(manifest["artifacts"]) == 9062,
            "trace manifest identity drift")
    boundaries = read_json(args.decode_boundaries)
    require(boundaries["status"] == "PASS", "decode boundaries not PASS")
    decoded = {int(row["decode_index"]): row for row in boundaries["decode_iterations"]}
    require(set(decoded) == {1, 2, 3}, "decode boundary matrix drift")
    require((decoded[1]["first_kernel_id"], decoded[1]["last_kernel_id"], decoded[1]["kernel_count"]) ==
            (2926, 4430, 1505), "D1 boundary drift")
    require((decoded[2]["first_kernel_id"], decoded[2]["last_kernel_id"], decoded[2]["kernel_count"]) ==
            (4431, 5935, 1505), "D2 boundary drift")

    sequence_rows = tsv(args.kernel_sequence)
    ids = [int(row["global_dynamic_order"]) for row in sequence_rows]
    require(ids == list(range(2926, 7441)), "full D1-D3 kernel sequence drift")
    d1_up = semantic_range(sequence_rows, 1, 0, "up_proj")
    d2_up = semantic_range(sequence_rows, 2, 0, "up_proj")
    require(d1_up["functions"][-1] == "awq_gemm_kernel" and d2_up["functions"][-1] == "awq_gemm_kernel",
            "up_proj semantic terminal kernel drift")
    first = int(decoded[1]["first_kernel_id"])
    last = d2_up["last_dynamic_kernel"]
    selected = [row for row in sequence_rows if first <= int(row["global_dynamic_order"]) <= last]
    require([int(row["global_dynamic_order"]) for row in selected] == list(range(first, last + 1)),
            "reuse window sequence not contiguous")
    require(all(int(row["decode_iteration"]) == 1 for row in selected[:1505]), "D1 incomplete")
    require(all(int(row["decode_iteration"]) == 2 for row in selected[1505:]), "D2 prefix drift")

    list_lines = [line.strip() for line in args.kernelslist.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    require(len(list_lines) == 4515, "full kernelslist count drift")
    expected_names = [f"kernel-{kernel_id}-" for kernel_id in range(first, last + 1)]
    selected_names = list_lines[:len(selected)]
    require(all(name.startswith(prefix) and name.endswith(".traceg.xz")
                for name, prefix in zip(selected_names, expected_names)),
            "kernelslist does not match dynamic sequence")

    args.stage.mkdir(parents=True, exist_ok=True)
    staged_list = args.stage / "kernelslist.g"
    staged_list.write_text("\n".join(selected_names) + "\n", encoding="utf-8")
    for name in selected_names:
        destination = args.stage / name
        source = args.trace_root / "traces" / name
        require(source.is_file(), f"missing trace artifact {source}")
        if destination.exists() or destination.is_symlink():
            require(destination.is_symlink() and destination.resolve() == source.resolve(),
                    f"staging collision {destination}")
        else:
            destination.symlink_to(source)

    header = list(sequence_rows[0])
    args.sequence_output.parent.mkdir(parents=True, exist_ok=True)
    with args.sequence_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(selected)

    trace_index = {int(row["global_dynamic_order"]): row for row in tsv(args.trace_index)}
    require(set(range(first, last + 1)).issubset(trace_index), "trace index missing reuse-window kernel")
    traceg_bytes = sum(int(trace_index[k]["size_bytes"]) for k in range(first, last + 1))
    instructions = sum(int(trace_index[k]["instructions"]) for k in range(first, last + 1))
    ctas = sum(int(trace_index[k]["thread_blocks"]) for k in range(first, last + 1))
    scope = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_WINDOW_SCOPE_V1",
        "run_id": RUN_ID, "source_manifest_sha256": MANIFEST_SHA,
        "source_sequence_sha256": sha256(args.kernel_sequence),
        "selected_sequence_sha256": sha256(args.sequence_output),
        "selected_kernelslist_sha256": sha256(staged_list),
        "first_dynamic_kernel": first, "last_dynamic_kernel": last,
        "total_kernel_count": len(selected), "D1_complete": True,
        "D1_first_kernel": decoded[1]["first_kernel_id"],
        "D1_last_kernel": decoded[1]["last_kernel_id"],
        "D1_kernel_count": decoded[1]["kernel_count"],
        "D2_first_kernel": decoded[2]["first_kernel_id"],
        "D2_prefix_complete": True, "D2_prefix_last_kernel": last,
        "D2_prefix_kernel_count": last - int(decoded[2]["first_kernel_id"]) + 1,
        "D1_L0_up_proj_range": d1_up, "D2_L0_up_proj_range": d2_up,
        "intervening_kernel_count": d2_up["first_dynamic_kernel"] - d1_up["last_dynamic_kernel"] - 1,
        "traceg_compressed_bytes": traceg_bytes,
        "dynamic_trace_instructions": instructions, "thread_blocks": ctas,
        "full_trace_payload_copied": False, "staging_method": "READ_ONLY_SYMLINKS",
        "no_kernel_filtering_or_reordering": True,
    }
    dump(args.output, scope)
    print(json.dumps({key: scope[key] for key in
                      ("first_dynamic_kernel", "last_dynamic_kernel", "total_kernel_count",
                       "traceg_compressed_bytes", "dynamic_trace_instructions", "thread_blocks")},
                     sort_keys=True))


def option_map(text: str):
    result = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or not line.startswith("-"):
            continue
        key, *rest = line.split(None, 1)
        result[key] = rest[0] if rest else ""
    return result


def build_configs(args) -> None:
    require(sha256(args.base_config) == PLATFORM_SHA, "platform config SHA drift")
    require(sha256(args.sidecar) == SIDECAR_SHA, "sidecar SHA drift")
    args.output.mkdir(parents=True, exist_ok=True)
    base = args.base_config.read_text(encoding="utf-8")
    common = ["-gpgpu_vm_mode 0",
              "-gpgpu_l2_oracle_elastic_diagnostics 0"]
    overlays = {
        "R0_BASELINE": common + [
            "-gpgpu_l2_oracle_elastic_qweight_enable 0",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 0",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0"],
        "M1_B16": common + [
            "-gpgpu_l2_oracle_elastic_qweight_enable 1",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 16777216",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0",
            f"-gpgpu_l2_oracle_elastic_interval_sidecar {args.sidecar}",
            f"-gpgpu_l2_oracle_elastic_sidecar_sha256 {SIDECAR_SHA}"],
        "M1_B16_DIAGNOSTIC": [common[0],
            "-gpgpu_l2_oracle_elastic_diagnostics 1",
            "-gpgpu_l2_oracle_elastic_qweight_enable 1",
            "-gpgpu_l2_oracle_elastic_protected_quota_bytes 16777216",
            "-gpgpu_l2_oracle_elastic_protected_quota_lines 0",
            f"-gpgpu_l2_oracle_elastic_interval_sidecar {args.sidecar}",
            f"-gpgpu_l2_oracle_elastic_sidecar_sha256 {SIDECAR_SHA}"],
    }
    outputs = {}
    maps = {}
    for name, overlay in overlays.items():
        path = args.output / f"{name}.gpgpusim.config"
        path.write_text(base.rstrip() + "\n\n# C16 E1 preregistered overlay\n" +
                        "\n".join(overlay) + "\n", encoding="utf-8")
        outputs[name] = path
        maps[name] = option_map(path.read_text(encoding="utf-8"))
    baseline, mechanism, diagnostic = maps["R0_BASELINE"], maps["M1_B16"], maps["M1_B16_DIAGNOSTIC"]
    def differences(left, right):
        keys = set(left) | set(right)
        return {key: [left.get(key), right.get(key)] for key in sorted(keys)
                if left.get(key) != right.get(key)}
    primary_diff = differences(baseline, mechanism)
    allowed_primary = {
        "-gpgpu_l2_oracle_elastic_qweight_enable",
        "-gpgpu_l2_oracle_elastic_protected_quota_bytes",
        "-gpgpu_l2_oracle_elastic_interval_sidecar",
        "-gpgpu_l2_oracle_elastic_sidecar_sha256",
    }
    require(set(primary_diff) == allowed_primary, f"unregistered primary config diff {primary_diff}")
    diagnostic_diff = differences(mechanism, diagnostic)
    require(set(diagnostic_diff) == {"-gpgpu_l2_oracle_elastic_diagnostics"},
            f"diagnostic config drift {diagnostic_diff}")
    trace_copy = args.output / "SM89_RTX4080_AWMA_V1.trace.config"
    shutil.copyfile(args.trace_config, trace_copy)
    matrix = {
        "status": "PASS", "schema": "C16_E1_B16_REUSE_RUN_MATRIX_V1",
        "core_parent_authority": CORE_HEAD, "core_execution_head": args.core_head,
        "framework_parent": FRAMEWORK_PARENT, "platform_config_sha256": PLATFORM_SHA,
        "trace_config_sha256": sha256(trace_copy), "sidecar_sha256": SIDECAR_SHA,
        "trace_scope_sha256": sha256(args.scope), "kernelslist_sha256": sha256(args.kernelslist),
        "runs": {name: {"condition": name, "config": str(path),
                         "config_sha256": sha256(path),
                         "primary_performance_authority": name in ("R0_BASELINE", "M1_B16"),
                         "diagnostic_only": name == "M1_B16_DIAGNOSTIC"}
                 for name, path in outputs.items()},
        "primary_config_diff": primary_diff, "diagnostic_config_diff": diagnostic_diff,
        "address_observer_enabled": False, "verbose_event_logging": False,
    }
    dump(args.matrix, matrix)
    print(json.dumps({"configs": {name: sha256(path) for name, path in outputs.items()}},
                     sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    scope = sub.add_parser("scope")
    scope.add_argument("--manifest", type=Path, required=True)
    scope.add_argument("--decode-boundaries", type=Path, required=True)
    scope.add_argument("--kernel-sequence", type=Path, required=True)
    scope.add_argument("--trace-index", type=Path, required=True)
    scope.add_argument("--kernelslist", type=Path, required=True)
    scope.add_argument("--trace-root", type=Path, required=True)
    scope.add_argument("--stage", type=Path, required=True)
    scope.add_argument("--sequence-output", type=Path, required=True)
    scope.add_argument("--output", type=Path, required=True)
    configs = sub.add_parser("configs")
    configs.add_argument("--base-config", type=Path, required=True)
    configs.add_argument("--trace-config", type=Path, required=True)
    configs.add_argument("--sidecar", type=Path, required=True)
    configs.add_argument("--scope", type=Path, required=True)
    configs.add_argument("--kernelslist", type=Path, required=True)
    configs.add_argument("--core-head", required=True)
    configs.add_argument("--output", type=Path, required=True)
    configs.add_argument("--matrix", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "scope":
        build_scope(args)
    else:
        build_configs(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
