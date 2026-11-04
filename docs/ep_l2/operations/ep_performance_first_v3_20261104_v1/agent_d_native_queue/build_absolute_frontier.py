"""Bounded registry-linked small accepted JSON only; no trace/raw scan or model."""
from pathlib import Path
import collections,csv,datetime,hashlib,json
ROOT=Path(__file__).parent
REG=Path("/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json")
CORES={"78f4b59e865b136eede74df74c44c210f5b4ca04","862376f62ab19f9a677abe31c6a422028b44fcd0"}
def sha(b):return hashlib.sha256(b).hexdigest()
def readref(ref):
 p=Path(ref["path"]);b=p.read_bytes()
 assert len(b)<=16<<20 and sha(b)==ref["sha256"],str(p)
 return json.loads(b)
def digest(obj):return sha(json.dumps(obj,sort_keys=True,separators=(",",":")).encode())
def main():
 rb=REG.read_bytes();r=json.loads(rb);rows=[];excluded=[];seen=set()
 for request,q in r["registered_future_requests"].items():
  if not request.startswith("EP_") or not isinstance(q.get("consumed"),dict):continue
  for cohort,row in q["consumed"].items():
   if row.get("state")!="CLOSED_ACCEPTED":
    excluded.append(dict(request=request,cohort=cohort,reason=row.get("state","unknown")));continue
   p=readref(row["accepted_point_ref"]);source=p["source_identity"]
   if source["core_source_commit"] not in CORES:
    excluded.append(dict(request=request,cohort=cohort,reason="OTHER_SOURCE_LINEAGE"));continue
   if p["uuid"] in seen:raise ValueError("duplicate accepted UUID")
   seen.add(p["uuid"]);s=readref(p["spec_ref"]);a=readref(row["archive_receipt_ref"])
   assert p["hardware_drained"] and s["source_identity"]==source and s["cohort"]==cohort
   assert s["input_identity_sha256"]==p["input_identity_sha256"]
   assert a["status"]=="TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS"
   assert len(a["native_restores"])==2
   opts=s["expected_effective_options"];assert len(opts)==282
   rows.append(dict(request=request,cohort=cohort,uuid=p["uuid"],program=s["program"],
    input_identity_sha256=p["input_identity_sha256"],core=source["core_source_commit"],
    ELF=source["binary_sha256"],Source5_SHA256=digest(source),source_identity=source,
    mode=p["mode"],profile=p["profile"],cycles=p["cycles"],instructions=p["instructions"],
    CTA=p["CTA"],kernel_count=p["kernel_count"],hardware_drained=True,
    clocks=opts["-gpgpu_clock_domains"],dram_latency=opts["-dram_latency"],
    geometry=s["geometry"],effective_282_SHA256=digest(opts),spec_ref=p["spec_ref"],
    accepted_point_ref=row["accepted_point_ref"],archive_receipt_ref=row["archive_receipt_ref"],
    observer_env=s.get("observer_env"),NI="NOT_UPGRADED_BY_THIS_DERIVATION",
    resource_cost="PROFILE_SPEC;NO_EQUAL_AREA_OR_UNIFORM_HARDWARE_CLAIM"))
 groups=collections.defaultdict(list)
 for row in rows:groups[(row["Source5_SHA256"],row["input_identity_sha256"],row["mode"])].append(row)
 frontier=[]
 for key,items in sorted(groups.items()):
  best=min(x["cycles"]for x in items);wins=[x for x in items if x["cycles"]==best]
  frontier.append(dict(Source5_SHA256=key[0],core=items[0]["core"],ELF=items[0]["ELF"],
   input_identity_sha256=key[1],program=items[0]["program"],mode=key[2],
   accepted_points=len(items),best_cycles=best,tied_best_cohorts=[x["cohort"]for x in wins],
   tied_best_profiles=[x["profile"]for x in wins],
   interpretation="PER_INPUT_PER_SOURCE_PER_MODE_MEASURED_MINIMUM_ACROSS_HARDWARE;NOT_UNIFIED_DESIGN"))
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (ROOT/"UNIFIED_ABSOLUTE_PERFORMANCE_FRONTIER_V3.json").write_text(json.dumps(dict(
  schema="EP_V3_BOUNDED_ACCEPTED_ABSOLUTE_FRONTIER_V1",utc=stamp,registry_observation_sha256=sha(rb),
  accepted_points=len(rows),frontier_groups=len(frontier),rows=rows,frontier=frontier,excluded=excluded,
  no_trace_or_raw_read=True,no_new_models=True,no_cross_Source5_performance_ratio=True,
  best_per_input_is_not_unified_hardware=True),indent=2)+"\n")
 keys=["program","input_identity_sha256","core","ELF","mode","profile","cycles","instructions",
 "CTA","kernel_count","clocks","dram_latency","geometry","effective_282_SHA256","cohort","uuid"]
 with (ROOT/"ABSOLUTE_ACCEPTED_POINTS_V3.csv").open("w",newline="")as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for row in sorted(rows,key=lambda x:(x["program"],x["core"],x["mode"],x["cycles"])):
   w.writerow({k:json.dumps(row[k],sort_keys=True)if isinstance(row[k],dict)else row[k]for k in keys})
 with (ROOT/"PER_INPUT_MODE_FRONTIER_V3.csv").open("w",newline="")as f:
  keys=["program","input_identity_sha256","core","ELF","mode","accepted_points","best_cycles",
  "tied_best_profiles","tied_best_cohorts","interpretation"]
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for row in frontier:w.writerow({k:json.dumps(row[k])if isinstance(row[k],list)else row[k]for k in keys})
 print(json.dumps(dict(accepted=len(rows),groups=len(frontier),excluded=len(excluded),
  source_counts=dict(collections.Counter(x["core"]for x in rows)))))
if __name__=="__main__":main()
