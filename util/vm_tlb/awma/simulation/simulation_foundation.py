#!/usr/bin/env python3
"""Fail-closed AWMA simulation consumer-side foundation utilities."""
from __future__ import annotations
import argparse, hashlib, json, lzma, sys
from pathlib import Path

SCHEMA_VERSION = "AWMA_SIM_FOUNDATION_V1"
SEMANTICS = ("pc", "opcode", "access_kind", "memory_space", "byte_width", "warp_id", "cta_id", "active_mask", "lane_addresses", "event_order", "sync_control")
FIELDS = ("workload_id", "target_id", "phase", "stream_context", "grid", "block", "trace_schema", "producer_source_sha256", "producer_binary_sha256", "address_context_sidecar", "asid_epoch", "va_width", "page_policy")
PREFIXES = ("tlb.", "ptw.", "pwc.", "walker.", "l1d.", "l2.", "dram.", "memory.", "queue.", "stall.", "performance.", "segment.", "selective.", "subentry.", "cache_variant.")
SCHEMAS={"SIM_INPUT":FIELDS,"SIM_BASELINE":("framework_sha","core_sha","binary_sha256","config_sha256","telemetry_schema"),"SIM_RUN":("sim_input_id","sim_baseline_id","config_sha256","execution_status"),"SIM_TELEMETRY_ROW":("metric_name","metric_value","unit","evidence_origin","scientific_status","claim_scope"),"SIM_COMPARISON_ROW":("baseline_sim_run_id","mechanism_sim_run_id","metric_name","metric_value","unit","claim_scope")}

class ContractError(ValueError): pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def stable_id(prefix, record):
    record = {k:v for k,v in record.items() if k not in ("id","sim_input_id","sim_baseline_id","sim_run_id")}
    return prefix + "_" + hashlib.sha256(canonical(record).encode()).hexdigest()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576), b""): h.update(chunk)
    return h.hexdigest()

def obj(path):
    try: value = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc: raise ContractError("invalid JSON %s: %s" % (path, exc))
    if not isinstance(value, dict): raise ContractError("JSON root must be object")
    return value

def need(record, fields, label):
    missing = [x for x in fields if record.get(x) in (None, "", [], {})]
    if missing: raise ContractError("%s missing: %s" % (label, ", ".join(missing)))

def identity_for(kind, record):
    if kind not in SCHEMAS: raise ContractError("unknown schema kind: "+kind)
    need(record, SCHEMAS[kind], kind)
    return stable_id(kind, record)

def member(root, name):
    if not isinstance(name,str) or not name or name.startswith("/") or ".." in Path(name).parts: raise ContractError("unsafe member")
    path = root / name
    if not path.is_file(): raise ContractError("missing member: %s" % name)
    return path

def validate_bundle(manifest_path):
    manifest = obj(manifest_path)
    if manifest.get("evidence_class") in ("C16WARP1","MREF_SHARDED_COMPLETE_SET") or manifest.get("simulator_eligibility") == "NOT_PROVEN_LOSSLESS":
        return {"admitted":False,"status":"NOT_PROVEN_LOSSLESS","sim_input_id":None,"reason":"C16WARP1/MREF is not a lossless simulator trace"}
    if manifest.get("schema_version") != SCHEMA_VERSION: raise ContractError("unsupported schema_version")
    need(manifest, FIELDS, "SIM_COMPAT_CAPTURE_V1 manifest")
    if manifest["trace_schema"] != "SIM_COMPAT_CAPTURE_V1": raise ContractError("unsupported trace_schema")
    semantics = manifest.get("instruction_semantics")
    if not isinstance(semantics,dict): raise ContractError("instruction_semantics must be object")
    need(semantics, SEMANTICS, "instruction_semantics")
    terminal = manifest.get("terminal")
    if not isinstance(terminal,dict) or terminal.get("status") != "COMPLETE": raise ContractError("terminal must be COMPLETE")
    if terminal.get("drop_count") != 0 or terminal.get("overflow_count") != 0: raise ContractError("drop/overflow must be zero")
    root, files = Path(manifest_path).parent, manifest.get("files")
    if not isinstance(files,dict) or not files: raise ContractError("files hash closure required")
    closure = {}
    for name, expected in files.items():
        actual = sha(member(root,name))
        if actual != expected: raise ContractError("hash mismatch: %s" % name)
        closure[name] = actual
    list_name = manifest.get("kernelslist")
    if list_name not in files: raise ContractError("kernelslist not hash-closed")
    traces = [x.strip() for x in member(root,list_name).read_text().splitlines() if x.strip()]
    if not traces: raise ContractError("empty kernelslist")
    for name in traces:
        if name not in files or not name.endswith(".traceg.xz"): raise ContractError("invalid trace list member: %s" % name)
        try:
            with lzma.open(member(root,name),"rb") as f:
                if not f.read(1): raise ContractError("empty trace")
        except lzma.LZMAError as exc: raise ContractError("malformed trace: %s" % name) from exc
    if manifest["address_context_sidecar"] not in files: raise ContractError("address sidecar not hash-closed")
    identity = {"schema_version":SCHEMA_VERSION,"manifest":{k:v for k,v in manifest.items() if k not in ("sim_input_id","files")},"files":closure}
    return {"admitted":True,"status":"ADMITTED","sim_input_id":stable_id("SIM_INPUT",identity),"trace_count":len(traces),"identity":identity}

def normalize(rows):
    answer, seen = [], set()
    for row in rows:
        need(row,("metric_name","metric_value","unit","evidence_origin","scientific_status","claim_scope"),"telemetry row")
        if not isinstance(row["metric_name"],str) or not row["metric_name"].startswith(PREFIXES): raise ContractError("unknown metric namespace")
        key=canonical(row)
        if key in seen: raise ContractError("conflicting/duplicate telemetry")
        seen.add(key); answer.append({**row,"schema_version":SCHEMA_VERSION})
    return sorted(answer,key=canonical)

def catalog_put(root, category, record):
    if not category.isidentifier(): raise ContractError("unsafe category")
    key=record.get("id") or record.get("sim_input_id") or record.get("sim_baseline_id") or record.get("sim_run_id")
    if not key: raise ContractError("record needs immutable ID")
    path=Path(root)/"entries"/category/(key+".json"); path.parent.mkdir(parents=True,exist_ok=True); encoded=canonical(record)+"\n"
    if path.exists():
        if path.read_text() != encoded: raise ContractError("conflicting same-ID content")
        return {"result":"NOOP_IDENTICAL","path":str(path)}
    path.write_text(encoded); return {"result":"CREATED","path":str(path)}

def snapshot(root, category):
    root=Path(root); d=root/"entries"/category
    rows=[{"path":str(p.relative_to(root)),"sha256":sha(p)} for p in sorted(d.glob("*.json"))] if d.exists() else []
    out={"schema_version":SCHEMA_VERSION,"category":category,"entries":rows}; out["snapshot_id"]=stable_id("SIM_SNAPSHOT",out)
    p=root/"snapshots"/(category+".json"); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(canonical(out)+"\n"); return out

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("admit"); a.add_argument("manifest")
    n=s.add_parser("normalize"); n.add_argument("source"); n.add_argument("output")
    c=s.add_parser("catalog-put"); c.add_argument("root"); c.add_argument("category"); c.add_argument("record")
    z=s.add_parser("snapshot"); z.add_argument("root"); z.add_argument("category")
    args=p.parse_args()
    try:
        if args.cmd=="admit": out=validate_bundle(args.manifest)
        elif args.cmd=="normalize":
            rows=json.loads(Path(args.source).read_text())
            if not isinstance(rows,list): raise ContractError("telemetry must be an array")
            val=normalize(rows); Path(args.output).write_text(canonical(val)+"\n"); out={"rows":len(val),"sha256":sha(args.output)}
        elif args.cmd=="catalog-put": out=catalog_put(args.root,args.category,obj(args.record))
        else: out=snapshot(args.root,args.category)
        print(json.dumps(out,sort_keys=True,indent=2)); return 0
    except ContractError as exc: print("CONTRACT_ERROR: "+str(exc),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
