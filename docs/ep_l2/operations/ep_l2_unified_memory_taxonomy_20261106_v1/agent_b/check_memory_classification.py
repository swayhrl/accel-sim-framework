from pathlib import Path
import json,hashlib
O=Path(__file__).parent
j=json.load(open(O/"MEMORY_RESOURCE_CLASSIFICATION.json"))
assert len(j["rows"])==103
assert sum(x["population_membership"]["member_ordinary96"] for x in j["rows"])==96
assert sum(x["population_membership"]["member_main35"] for x in j["rows"])==35
assert sum(x["population_membership"]["member_main42"] for x in j["rows"])==42
assert sum(bool(x["endpoints"]) for x in j["rows"])==27
checks=5
for row in j["rows"]:
 for e in row["endpoints"]:
  ro=e["RO"]
  if ro["status"]=="MEASURED_FINAL64_STRUCTURED_SEALED_BUNDLE":
   t=ro["totals"];assert t["transactions"]+t["merges"]==t["accepted_ro"];checks+=1
   if t["accepted_ro"]==0:assert ro["merge_ratio"]["value"] is None;checks+=1
  assert e["labels"]["tag_reserved_pressure"]=="UNKNOWN";checks+=1
  # Missing typed per-address data never becomes measured zero.
  if e["per_address"]["observed_blocking"] is None:assert e["labels"]["per_address_pressure"]=="UNKNOWN";checks+=1
 if not row["endpoints"]:assert row["classification_status"]=="UNKNOWN_NO_REFERENCE_ENDPOINT";checks+=1
for r in j["input_refs"]:
 assert hashlib.sha256(Path(r["path"]).read_bytes()).hexdigest()==r["sha256"];checks+=1
conv=next(x for x in j["rows"] if x["program"]=="convolutionSeparable")
f=next(x for x in conv["endpoints"] if x["mode"]=="F")
assert f["RO"]["totals"]["concurrent_duplicate_sectors"]==1 and not f["conflicts"];checks+=1
s=next(x for x in j["rows"] if x["program"]=="sgemm")
assert next(x for x in s["endpoints"] if x["mode"]=="F")["RO"]["merge_ratio"]["value"]>0.9
assert all(x["labels"]["ordinary_line_MSHR_pressure"]=="NO_SATURATION_OBSERVED" for x in s["endpoints"]);checks+=1
v=next(x for x in j["rows"] if x["input_identity_sha256"]=="ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc")
assert v["RO_policy_activation"]=="MEASURED_NOT_ACTIVATED_VECTOR1700_POLICY1";checks+=1
assert len(v["source812_accepted_layers"])==2;checks+=1
# Guard against common invalid causal joins: each rejected change is independent.
def admissible(a,b):
 fields=["input","source5","ordered","mode","clock-independent-options"]
 return all(a.get(k)==b.get(k) for k in fields)
a={"input":"shaA","source5":["core","framework","vendor","ELF","lib"],"ordered":"populationA","mode":"F","clock-independent-options":{"Tag":"32x8"}}
assert admissible(a,dict(a));checks+=1
import copy
for field in a:
 b=copy.deepcopy(a);b[field]="different";assert not admissible(a,b);checks+=1
print(json.dumps({"status":"PASS","checks":checks,"new_models":0,"raw_trace_reads":0}))
