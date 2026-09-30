#!/usr/bin/env python3
"""Nsight SQLite helpers for correlation-authoritative FFN timeline capture."""

import hashlib
import json
import re
import sqlite3

PROJ_RE = re.compile(r"^C16_E1_OPF_CONTROL_GUD84_L(\d+)_(GATE_PROJ|UP_PROJ|DOWN_PROJ)_D(\d+)$")
EXTRA_RE = re.compile(r"^C16_FFN_TIMELINE_L(\d+)_D(\d+)_(ACTIVATION|MULTIPLY)$")
DECODE_WALL = "C16_FFN_TIMELINE_DECODE_D0_D3"


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def connect(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def string_map(conn):
    return {int(i): value for i, value in conn.execute("SELECT id,value FROM StringIds")}


def kernel_rows(conn):
    strings = string_map(conn)
    query = """
      SELECT rowid,start,end,deviceId,contextId,streamId,correlationId,globalPid,
             demangledName,shortName,gridX,gridY,gridZ,blockX,blockY,blockZ
      FROM CUPTI_ACTIVITY_KIND_KERNEL ORDER BY start,rowid
    """
    rows = []
    for row in conn.execute(query):
        (rowid,start,end,device,context,stream,corr,gpid,demangled,short,
         gx,gy,gz,bx,by,bz) = row
        name = strings.get(demangled) or strings.get(short) or "[UNRESOLVED_KERNEL]"
        rows.append({"rowid": int(rowid), "start": int(start), "end": int(end),
                     "device": int(device), "context": int(context), "stream": int(stream),
                     "correlation_id": int(corr), "global_pid": int(gpid), "kernel_name": name,
                     "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}"})
    return rows


def runtime_by_correlation(conn):
    strings = string_map(conn)
    query = """
      SELECT rowid,start,end,globalTid,correlationId,nameId
      FROM CUPTI_ACTIVITY_KIND_RUNTIME ORDER BY start,rowid
    """
    out = {}
    for rowid,start,end,gtid,corr,name_id in conn.execute(query):
        out[int(corr)] = {"rowid": int(rowid), "start": int(start), "end": int(end),
                          "global_tid": int(gtid), "correlation_id": int(corr),
                          "api_name": strings.get(name_id, "[UNRESOLVED_CUDA_API]")}
    return out


def nvtx_ranges(conn):
    strings = string_map(conn)
    query = """
      SELECT rowid,start,end,text,globalTid,textId,eventType
      FROM NVTX_EVENTS WHERE end IS NOT NULL ORDER BY start,rowid
    """
    rows = []
    for rowid,start,end,text,gtid,text_id,event_type in conn.execute(query):
        label = text if isinstance(text, str) and text else strings.get(text_id)
        if not label:
            continue
        rows.append({"rowid": int(rowid), "start": int(start), "end": int(end),
                     "global_tid": int(gtid), "event_type": int(event_type), "label": label})
    return rows


def parse_semantic(label):
    match = PROJ_RE.fullmatch(label)
    if match:
        return {"layer": int(match.group(1)), "role": match.group(2).lower(),
                "decode_step": int(match.group(3))}
    match = EXTRA_RE.fullmatch(label)
    if match:
        return {"layer": int(match.group(1)), "role": match.group(3).lower(),
                "decode_step": int(match.group(2))}
    return None


def kernel_signature(sqlite_path):
    conn = connect(sqlite_path)
    try:
        return [(r["kernel_name"], r["grid"], r["block"]) for r in kernel_rows(conn)]
    finally:
        conn.close()


def canonical_occurrences(run):
    keys = ("layer", "role", "decode_index", "token_id", "range", "input_sha256",
            "output_sha256", "input_shape", "output_shape", "module_class")
    return [{key: row[key] for key in keys} for row in run["occurrences"]]


def semantic_policy(run):
    keys = ("condition", "mode", "set_name", "selected_roles", "selected_module_count",
            "hit_ratio", "target_persisting", "policy_transition_count",
            "all_84_ffn_instrumented", "no_reset_between_transitions", "no_inner_loop_synchronize")
    return {key: run[key] for key in keys}
