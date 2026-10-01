#!/usr/bin/env python3
"""CPU-only synthetic tests for interval union, chronology, and source guards."""

import argparse
import ast
import hashlib
import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path


V1_SHA = "1f68c1117623cbc46f98f51f17ba798d8bf5ffb103f427b9d7b916ced0a35020"
V2_SHA = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_name(node):
    value = node.func
    parts = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def named(tree, kind, name):
    rows = [node for node in ast.walk(tree) if isinstance(node, kind) and node.name == name]
    assert len(rows) == 1
    return rows[0]


def build_fixture(sqlite_path):
    con = sqlite3.connect(sqlite_path)
    con.execute("create table StringIds(id integer, value text)")
    con.executemany("insert into StringIds values(?,?)", [(1, "cudaLaunchKernel"), (2, "kernel_A"), (3, "kernel_B")])
    con.execute("create table NVTX_EVENTS(start integer,end integer,eventType integer,rangeId integer,category integer,color integer,text text,globalTid integer,endGlobalTid integer,textId integer,domainId integer,uint64Value integer,int64Value integer,doubleValue real,uint32Value integer,int32Value integer,floatValue real,jsonTextId integer,jsonText text,binaryData blob)")
    con.executemany("insert into NVTX_EVENTS(start,end,eventType,text,globalTid) values(?,?,?,?,?)", [
        (100, 1000, 59, "C16_TIER0_MP02_GRAPH_OFF_OBSERVED", 7),
        (150, 450, 59, "C16_STAGEA_0_model.layers.0.self_attn", 7),
        (500, 900, 59, "C16_STAGEA_1_model.layers.0.mlp.gate_up_proj", 7),
    ])
    con.execute("create table CUPTI_ACTIVITY_KIND_RUNTIME(start integer,end integer,eventClass integer,globalTid integer,correlationId integer,nameId integer,returnValue integer,callchainId integer)")
    con.executemany("insert into CUPTI_ACTIVITY_KIND_RUNTIME values(?,?,?,?,?,?,?,?)", [
        (200, 210, 0, 7, 10, 1, 0, 0),
        (550, 560, 0, 7, 11, 1, 0, 0),
    ])
    con.execute("create table CUPTI_ACTIVITY_KIND_KERNEL(start integer,end integer,deviceId integer,contextId integer,greenContextId integer,streamId integer,correlationId integer,globalPid integer,demangledName integer,shortName integer,mangledName integer,launchType integer,cacheConfig integer,registersPerThread integer,gridX integer,gridY integer,gridZ integer,blockX integer,blockY integer,blockZ integer,staticSharedMemory integer,dynamicSharedMemory integer,localMemoryPerThread integer,localMemoryTotal integer,gridId integer,sharedMemoryExecuted integer,graphNodeId integer,sharedMemoryLimitConfig integer)")
    base = [0] * 28
    rows = []
    for start, end, corr, name in ((300, 400, 10, 2), (600, 800, 11, 3)):
        row = base.copy()
        row[0], row[1], row[5], row[6], row[8], row[9] = start, end, 1, corr, name, name
        row[14:20] = [1, 1, 1, 32, 1, 1]
        rows.append(row)
    con.executemany("insert into CUPTI_ACTIVITY_KIND_KERNEL values(" + ",".join("?" * 28) + ")", rows)
    con.commit()
    con.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    root = repo / "util/vm_tlb/c16/stagea_dense_first_tier0"
    v1 = repo / "util/vm_tlb/c16/stagea_runtime_qualification/runner.py"
    v2 = root / "observer_v2_authority.py"
    assert sha(v1) == V1_SHA
    assert sha(v2) == V2_SHA
    for path, expected in ((v1, 2), (v2, 0)):
        tree = ast.parse(path.read_text())
        hook = named(tree, ast.ClassDef, "HookSession")
        calls = [call_name(node) for node in ast.walk(hook) if isinstance(node, ast.Call)]
        assert calls.count("torch.cuda.Event") == expected
        assert calls.count("torch.cuda.nvtx.range_push") == 1
        assert calls.count("torch.cuda.nvtx.range_pop") == 1
    tier_tree = ast.parse((root / "runner.py").read_text())
    invoke = named(tier_tree, ast.FunctionDef, "invoke")
    calls = [call_name(node) for node in ast.walk(invoke) if isinstance(node, ast.Call)]
    assert calls.count("torch.cuda.Event") == 2

    with tempfile.TemporaryDirectory(prefix="c16_tier0_fixture_") as name:
        temp = Path(name)
        sqlite_path = temp / "fixture.sqlite"
        trace = temp / "fixture.nsys-rep"
        trace.write_bytes(b"synthetic fixture")
        build_fixture(sqlite_path)
        observed = {
            "batch_size": 1,
            "samples": [{"instrumentation": {"semantic_order": [
                {"ordinal": 0, "module": "model.layers.0.self_attn", "input_shape": [512, 2048], "output_shape": [512, 2048]},
                {"ordinal": 1, "module": "model.layers.0.mlp.gate_up_proj", "input_shape": [1, 2048], "output_shape": [1, 11008]},
            ]}}],
        }
        observed_path = temp / "observed.json"
        observed_path.write_text(json.dumps(observed))
        subprocess.run([
            "python3", str(root / "nsys_extract.py"), "--point", "MP02",
            "--trace", str(trace), "--sqlite-input", str(sqlite_path),
            "--observed-json", str(observed_path), "--output-dir", str(temp / "out"),
        ], cwd=repo, check=True, stdout=subprocess.PIPE, text=True)
        receipt = json.loads((temp / "out/MP02_NSYS_PARSE_RECEIPT.json").read_text())
        assert receipt["status"] == "PASS"
        assert receipt["semantic_range_count"] == 2
        assert receipt["kernel_count_in_parent"] == 2
        assert receipt["parent_cuda_interval_union_ns"] == 300
        assert receipt["positive_launch_gap_union_ns"] == 200
    print(json.dumps({"status": "PASS", "v1_sha256": V1_SHA, "v2_sha256": V2_SHA,
                      "fixture_parent_union_ns": 300, "fixture_positive_gap_ns": 200}, sort_keys=True))


if __name__ == "__main__":
    main()
