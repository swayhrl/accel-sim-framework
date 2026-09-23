#!/usr/bin/env python3
"""Fail-closed isolated L2-persistence timing and raw NCU consumer."""
from __future__ import annotations

import csv, hashlib, json, math, re, statistics
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

class IsolatedConsumerError(ValueError): pass

CONDITIONS = ("ISO_BASELINE_DENSE", "ISO_QWEIGHT_PERSIST_DENSE")
METRICS = ("l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

def _text(v, name):
    if not isinstance(v, str) or not v.strip(): raise IsolatedConsumerError(f"missing {name}")
    return v.strip()

def _integer(v, name, minimum=0):
    if isinstance(v, bool): raise IsolatedConsumerError(f"invalid {name}")
    s = str(v).strip()
    try: n = int(s)
    except (TypeError, ValueError) as e: raise IsolatedConsumerError(f"invalid {name}") from e
    if s != str(n) or n < minimum: raise IsolatedConsumerError(f"invalid {name}")
    return n

def _sha(v, name):
    s = _text(v, name).lower()
    if not HEX64.fullmatch(s): raise IsolatedConsumerError(f"invalid {name}")
    return s

def _sha_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""): h.update(b)
    return h.hexdigest()

def _stats(items):
    vals = [v for _, v in sorted(items)]; mean = statistics.fmean(vals)
    return {"sample_count":len(vals), "samples_ms":vals, "min_ms":min(vals),
            "median_ms":statistics.median(vals), "max_ms":max(vals),
            "mean_ms":mean, "cv":statistics.pstdev(vals)/mean}

def analyze_timing_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    grouped, shas, seen = defaultdict(list), {}, set()
    for r in rows:
        c = _text(r.get("condition"), "condition")
        if c not in CONDITIONS: raise IsolatedConsumerError("wrong condition")
        if (_text(r.get("role"), "role"), _integer(r.get("M"), "M", 1),
            _text(r.get("implementation"), "implementation")) != ("up_proj",1,"AWQ_FP16_INPUT"):
            raise IsolatedConsumerError("wrong semantic target")
        rep = _integer(r.get("rep"), "rep")
        if (c,rep) in seen: raise IsolatedConsumerError("duplicate rep")
        seen.add((c,rep))
        try: value = float(r.get("timing_ms"))
        except (TypeError,ValueError) as e: raise IsolatedConsumerError("invalid timing") from e
        if not math.isfinite(value) or value <= 0: raise IsolatedConsumerError("invalid timing")
        pair = (_sha(r.get("input_sha256"),"input_sha256"), _sha(r.get("output_sha256"),"output_sha256"))
        if c in shas and shas[c] != pair: raise IsolatedConsumerError("SHA drift within condition")
        shas[c] = pair; grouped[c].append((rep,value))
    if set(grouped) != set(CONDITIONS) or len(set(shas.values())) != 1:
        raise IsolatedConsumerError("condition matrix or cross-condition SHA mismatch")
    out, rep_sets = {}, []
    for c in CONDITIONS:
        rs = frozenset(x for x,_ in grouped[c]); rep_sets.append(rs)
        if len(grouped[c]) != 9 or rs not in {frozenset(range(9)),frozenset(range(1,10))}:
            raise IsolatedConsumerError("expected exactly 9 reps")
        out[c] = _stats(grouped[c])
    if rep_sets[0] != rep_sets[1]: raise IsolatedConsumerError("rep indexing drift")
    ratio = out[CONDITIONS[1]]["median_ms"] / out[CONDITIONS[0]]["median_ms"]
    return {"status":"PASS", "authority":"RAW_PER_REPETITION_TIMING_ROWS_ONLY",
            "input_sha256":next(iter(shas.values()))[0], "output_sha256":next(iter(shas.values()))[1],
            "conditions":out, "persist_over_baseline_timing_ratio":ratio}

def _option(text, opt):
    return re.findall(rf"(?:^|\s){re.escape(opt)}(?:=|\s+)([^\s\"']+)", text, re.M)

def _session(path, spec):
    text = path.read_text(encoding="utf-8")
    if set(_option(text,"--replay-mode")) != {"application"}: raise IsolatedConsumerError("replay mismatch")
    if set(_option(text,"--cache-control")) != {"none"}: raise IsolatedConsumerError("cache mismatch")
    if {x.rstrip('/') for x in _option(text,"--nvtx-include")} != {spec["range_name"]}: raise IsolatedConsumerError("range mismatch")
    sets = set(_option(text,"--metrics"))
    if len(sets)!=1 or set(next(iter(sets)).split(',')) != set(METRICS): raise IsolatedConsumerError("metrics mismatch")
    return {"sha256":_sha_file(path),"replay_mode":"application","cache_control":"none"}

def _profile(path,spec):
    receipts=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        try: x=json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(x,dict) and x.get("status")=="PASS": receipts.append(x)
    if len(receipts)!=1: raise IsolatedConsumerError("PROFILE needs exactly one PASS receipt")
    r=receipts[0]
    expected={"condition":spec["condition"],"role":"up_proj","M":1,"implementation":"AWQ_FP16_INPUT",
              "range":spec["range_name"],"input_sha256":spec["input_sha256"],"output_sha256":spec["output_sha256"]}
    if any(r.get(k)!=v for k,v in expected.items()): raise IsolatedConsumerError("PROFILE identity mismatch")
    return {"sha256":_sha_file(path),**expected}

def _decimal(v,name):
    try: x=Decimal(v.replace(',','').strip())
    except (InvalidOperation,AttributeError) as e: raise IsolatedConsumerError(f"invalid {name}") from e
    if not x.is_finite() or x<0: raise IsolatedConsumerError(f"invalid {name}")
    return x

def _base(path,spec):
    with path.open(newline='',encoding='utf-8-sig') as f: table=list(csv.reader(f))
    if len(table)<3: raise IsolatedConsumerError("short BASE")
    header,units=table[:2]
    if len(header)!=len(set(header)) or len(units)!=len(header): raise IsolatedConsumerError("bad BASE schema")
    idx={v:i for i,v in enumerate(header)}
    req={"ID","Process ID","Kernel Name","profiler__replayer_passes",*METRICS}
    if req-set(idx): raise IsolatedConsumerError("missing BASE columns")
    rc=[i for i,x in enumerate(header) if "Push/Pop_Range" in x]
    if len(rc)!=1: raise IsolatedConsumerError("ambiguous range column")
    if any(units[idx[m]].strip()!='byte' for m in METRICS): raise IsolatedConsumerError("unit mismatch")
    pat=re.compile(r"(?:^|:)"+re.escape(spec["range_name"])+r"(?=:|/|$)")
    rows=[r for r in table[2:] if len(r)==len(header) and r[idx['ID']].strip() and len(pat.findall(r[rc[0]].strip()))==1]
    if not rows: raise IsolatedConsumerError("no exact target rows")
    if len({r[idx['Process ID']].strip() for r in rows})!=1: raise IsolatedConsumerError("process mismatch")
    ids,names=set(),[]; totals={m:Decimal(0) for m in METRICS}
    for r in rows:
        kid,name=r[idx['ID']].strip(),r[idx['Kernel Name']].strip()
        if not kid or not name or kid in ids: raise IsolatedConsumerError("duplicate kernel")
        ids.add(kid); names.append(name)
        if _decimal(r[idx['profiler__replayer_passes']],"passes") != Decimal(spec["expected_pass_count"]): raise IsolatedConsumerError("pass mismatch")
        for m in METRICS: totals[m]+=_decimal(r[idx[m]],m)
    if len(names)!=len(spec["expected_kernel_names"]) or set(names)!=set(spec["expected_kernel_names"]): raise IsolatedConsumerError("kernel inventory mismatch")
    return {"base_sha256":_sha_file(path),"kernel_names":names,"metric_unit":"byte","metric_sums":{m:str(v) for m,v in totals.items()}}

def _policy(receipt, **kwargs):
    try: from .policy_receipt import validate_policy_receipt
    except ImportError: from policy_receipt import validate_policy_receipt
    return validate_policy_receipt(receipt,**kwargs)

def consume_ncu(document: Mapping[str,Any], root=Path('.'), *, policy_validator: Callable|None=None):
    if document.get("schema_version")!=1 or not isinstance(document.get("profiles"),list): raise IsolatedConsumerError("bad spec")
    specs=[]
    for raw in document["profiles"]:
        c=_text(raw.get("condition"),"condition")
        if c not in CONDITIONS: raise IsolatedConsumerError("wrong condition")
        if (_text(raw.get("role"),"role"),_integer(raw.get("M"),"M",1),_text(raw.get("implementation"),"implementation")) != ("up_proj",1,"AWQ_FP16_INPUT"): raise IsolatedConsumerError("wrong target")
        s={"condition":c,"range_name":_text(raw.get("range_name"),"range_name"),
           "input_sha256":_sha(raw.get("input_sha256"),"input_sha256"),"output_sha256":_sha(raw.get("output_sha256"),"output_sha256"),
           "expected_kernel_names":raw.get("expected_kernel_names"),"expected_pass_count":_integer(raw.get("expected_pass_count"),"expected_pass_count",1),
           "expected_target":_text(raw.get("expected_target"),"expected_target"),"expected_budget_bytes":raw.get("expected_budget_bytes")}
        if not isinstance(s["expected_kernel_names"],list) or not s["expected_kernel_names"] or len(s["expected_kernel_names"])!=len(set(s["expected_kernel_names"])): raise IsolatedConsumerError("bad kernel inventory")
        for k in ("base","session","profile","policy_receipt"):
            p=root/_text(raw.get(k+"_path"),k+"_path")
            if not p.is_file(): raise IsolatedConsumerError("missing raw file")
            s[k+"_path"]=p
        specs.append(s)
    if [s["condition"] for s in specs].count(CONDITIONS[0])!=1 or [s["condition"] for s in specs].count(CONDITIONS[1])!=1: raise IsolatedConsumerError("wrong two-condition matrix")
    if len({(s['input_sha256'],s['output_sha256']) for s in specs})!=1: raise IsolatedConsumerError("NCU SHA mismatch")
    validator=policy_validator or _policy; profiles=[]
    for s in specs:
        receipt=json.loads(s["policy_receipt_path"].read_text(encoding="utf-8"))
        kwargs={"expected_condition":s["condition"],"expected_target":s["expected_target"]}
        if s["expected_budget_bytes"] is not None: kwargs["expected_budget_bytes"]=_integer(s["expected_budget_bytes"],"expected_budget_bytes")
        try: policy=validator(receipt,**kwargs)
        except Exception as e: raise IsolatedConsumerError(f"policy receipt invalid: {e}") from e
        if not isinstance(policy,dict) or policy.get("status")!="PASS": raise IsolatedConsumerError("policy not PASS")
        profiles.append({"semantic_identity":{"condition":s["condition"],"role":"up_proj","M":1,"implementation":"AWQ_FP16_INPUT"},
                         "range_name":s["range_name"],"input_sha256":s["input_sha256"],"output_sha256":s["output_sha256"],
                         "session":_session(s["session_path"],s),"profile_log":_profile(s["profile_path"],s),
                         "policy_receipt":{"sha256":_sha_file(s["policy_receipt_path"]),"validation":policy},**_base(s["base_path"],s)})
    by={p['semantic_identity']['condition']:p for p in profiles}; ratios={}
    for m in METRICS:
        b=Decimal(by[CONDITIONS[0]]['metric_sums'][m]); p=Decimal(by[CONDITIONS[1]]['metric_sums'][m])
        ratios[m]={"persist_over_baseline":None if b==0 else float(p/b),"absolute_change":str(p-b),"ratio_status":"UNDEFINED_ZERO_DENOMINATOR" if b==0 else "PASS"}
    return {"status":"PASS","authority":"DIRECT_RAW_BASE_SESSION_PROFILE_POLICY_RECEIPT_ONLY","profiles":profiles,"persist_over_baseline_metric_effects":ratios}
