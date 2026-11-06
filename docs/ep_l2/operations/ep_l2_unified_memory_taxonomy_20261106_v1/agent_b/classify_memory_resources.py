import json,hashlib,pathlib,collections,datetime,csv
B=pathlib.Path("/root/data/ep_l2_full_workload_performance_20261027_v1");O=B/"research/unified_memory_taxonomy_20261106_v1/agent_b";V=B/"research/performance_first_v5_20261105_v1"
FEATURE=B/"research/observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json"
OLD=B/"agent_b/results_analysis_20261028_v1/versions/20261029T013310Z_2f341af0/RESULTS_ANALYSIS_CURRENT.json"
def ref(p):
 p=pathlib.Path(p);return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.load(open(p))
refs={}
def pin(p):
 r=ref(p);refs[str(p)]=r;return r
f=load(FEATURE);old=load(OLD);pin(FEATURE);pin(OLD)
def measured(v,zero_label,present_label):
 return "UNKNOWN" if v is None else zero_label if v==0 else present_label
def endpoint(e):
 m=e.get("ordinary_MSHR",{});ro=e.get("RO_M",{});w=e.get("W",{});conflicts=[]
 s=load(e["spec_ref"]["path"]);assert ref(e["spec_ref"]["path"])["sha256"]==e["spec_ref"]["sha256"];pin(e["spec_ref"]["path"])
 options=s["expected_effective_options"]
 result={k:e.get(k) for k in ["cohort","mode","source_identity","geometry","cycles","semantic_population_digest","spec_ref","validation_ref","RO_qualification_ref","RO_applicability"]}
 result["hardware"]={k:options.get(k) for k in ["-gpgpu_clock_domains","-dram_latency","-gpgpu_cache:dl2","-gpgpu_ep_l2_descriptor_pool_size","-gpgpu_ep_l2_descriptor_per_line_cap","-gpgpu_ep_l2_ro_tag_detach","-gpgpu_ep_l2_ro_line_mshr_bypass"]}
 result["ordinary_line_MSHR"]={k:m.get(k) for k in ["line_max_over_slices","line_full_events_sum","line_full_head_observations_sum","line_eligible_sum","line_semantic_need_sum","slices_peak_eq128","slices_line_full_positive"]}
 result["descriptor"]={k:m.get(k) for k in ["descriptor_max_over_slices","descriptor_full_events_sum"]}
 result["per_address"]={"capacity":32,"observed_blocking":m.get("head_reasons",{}).get("PER_ADDRESS_CAP"),"status":"UNKNOWN_UNLESS_TYPED_HEAD_PROJECTION_PRESENT"}
 result["tag_reserved"]={"status":"UNKNOWN_NO_JOINT_CERTIFIED_HEAD_TAG_RESERVED_TIMED_FRONTEND_MEASUREMENT","heavy_observer":e.get("T",{}).get("heavy_tag_observer"),"T_enabled":e.get("T",{}).get("enabled")}
 result["old_RO_projection"]=ro
 result["RO"]={"status":"NOT_APPLICABLE" if e["mode"]!="F" else "UNKNOWN","strict_fill_before_ready":"NOT_COLLECTED","lower_sectors_semantics":"issued RO lower sectors, not completed DRAM bandwidth"}
 if e["mode"]=="F":
  br=e["validation_ref"];pin(br["path"]);assert refs[br["path"]]["sha256"]==br["sha256"]
  bundle=load(br["path"]);assert bundle["source_identity"]==e["source_identity"]
  assert bundle["input_identity_sha256"]==s["input_identity_sha256"]
  records=bundle.get("model",{}).get("mechanism_metrics",{}).get("full_mechanism_records",{}).get("readonly",{})
  if records:
   assert len(records)==64 and set(records)=={str(x) for x in range(64)}
   keys=["accepted_global_reads","accepted_oracle_candidates","accepted_ro","transactions","merges","detached","concurrent_duplicate_sectors","responses","lower_sectors"]
   totals={k:sum(v["summary"].get(k,0) for v in records.values()) for k in keys}
   assert totals["transactions"]+totals["merges"]==totals["accepted_ro"]
   result["RO"].update({"status":"MEASURED_FINAL64_STRUCTURED_SEALED_BUNDLE","totals":totals,"source_ref":br,"aggregation":"one already-selected final cumulative record per slice; no raw reread","merge_ratio":{"numerator":totals["merges"],"denominator":totals["accepted_ro"],"value":totals["merges"]/totals["accepted_ro"] if totals["accepted_ro"] else None,"population":"accepted RO requester admissions, not all reads/ingress/unique lines","complete":True},"peak_live_transactions_max_over_slices":max(v["resource"].get("peak_transactions",0) for v in records.values()),"peak_issued_lower_transactions_max_over_slices":max(v.get("lower_concurrency",{}).get("peak_lower_transactions",0) for v in records.values()),"query_count":sum(v["resource"].get("query_count",0) for v in records.values()),"query_wait_observations_sum":sum(v["resource"].get("query_wait_cycles",0) for v in records.values())})
   if ro.get("status")=="OBSERVED" and ro.get("duplicate_sectors") is not None and ro["duplicate_sectors"]!=totals["concurrent_duplicate_sectors"]:
    conflicts.append({"field":"concurrent_duplicate_sectors","old_projection":ro["duplicate_sectors"],"sealed_bundle_final64":totals["concurrent_duplicate_sectors"],"resolution":"retain both; old projection is not zero-duplicate evidence; no history rewrite"})
  else:result["RO"]["gap"]="No typed readonly final records in small bundle; UNKNOWN"
 result["W"]={"wb_created":w.get("wb_created"),"wad_max":w.get("wad_max"),"WBUF_peak":w.get("WBUF_peak_max_over_slices"),"WB_DATA_SPACE":w.get("head_reasons",{}).get("WB_DATA_SPACE"),"WAD_FULL":w.get("head_reasons",{}).get("WAD_FULL")}
 result["labels"]={"ordinary_line_MSHR_pressure":measured(m.get("line_full_events_sum"),"NO_SATURATION_OBSERVED","ACTUAL_SATURATION_OBSERVED"),"descriptor_pressure":measured(m.get("descriptor_full_events_sum"),"NO_SATURATION_OBSERVED","ACTUAL_SATURATION_OBSERVED"),"RO_traffic":measured(result["RO"].get("totals",{}).get("accepted_ro"),"NO_ACCEPTED_RO","ACCEPTED_RO_TRAFFIC_OBSERVED"),"tag_reserved_pressure":"UNKNOWN","per_address_pressure":"UNKNOWN","Core812_activation_from_this_endpoint":"UNKNOWN_DIFFERENT_SOURCE_OR_POLICY_TRACE"}
 result["conflicts"]=conflicts;result["confidence"]="HIGH_EXACT_FROZEN_ENDPOINT_METRICS_NOT_CAUSAL_INFERENCE"
 return result
rows=[]
for n,r in enumerate(f["rows"]):
 eps=[endpoint(e) for e in r.get("reference_endpoints",[])]
 rows.append({"original_row_index":n,"program":r["program"],"program_id":r.get("program_id"),"input_identity_sha256":r.get("input_identity_sha256"),"population_membership":{k:r.get(k) for k in ["member_ordinary96","member_main35","member_main42"]},"endpoints":eps,"memory_service_sensitivity":{"status":"UNKNOWN_NO_MATCHED_SERVICE_PERTURBATION"},"RO_policy_activation":"UNKNOWN_NOT_MEASURED_ON_SOURCE812" if eps else "UNKNOWN_UNMEASURED_INPUT","classification_status":"ENDPOINT_METRICS_AVAILABLE" if eps else "UNKNOWN_NO_REFERENCE_ENDPOINT","gaps":["No causal critical-path attribution from cumulative waits","No common-source configuration-independent personality claim"]})
# Reuse only accepted frequency perturbations, exact input+Source5+ordered population+mode+other effective options equal.
for row in rows:
 ident=row["input_identity_sha256"]
 base=[e for e in old["endpoints"] if e.get("accepted") and e.get("input_identity_sha256")==ident and e.get("profile")=="REF32x8_L100"]
 fast=[e for e in old["endpoints"] if e.get("accepted") and e.get("input_identity_sha256")==ident and e.get("profile")=="D_DRAM_MHZ1020"]
 sensitivities=[]
 for c in fast:
  matches=[e for e in base if e["mode"]==c["mode"] and e["source_identity"]==c["source_identity"] and e["semantic_population_digest"]==c["semantic_population_digest"]]
  assert len(matches)==1
  a=matches[0];sa=load(a["spec_ref"]["path"]);sc=load(c["spec_ref"]["path"]);pin(a["spec_ref"]["path"]);pin(c["spec_ref"]["path"])
  oa=sa["expected_effective_options"];oc=sc["expected_effective_options"];diff={k:[oa.get(k),oc.get(k)] for k in set(oa)|set(oc) if oa.get(k)!=oc.get(k)}
  assert set(diff)=={"-gpgpu_clock_domains"},diff
  sensitivities.append({"mode":a["mode"],"Source5":a["source_identity"],"reference_cohort":a["cohort"],"candidate_cohort":c["cohort"],"reference_spec_ref":a["spec_ref"],"candidate_spec_ref":c["spec_ref"],"semantic_population_digest":a["semantic_population_digest"],"option_diff":diff,"cycles_850":a["cycles"],"cycles_1020":c["cycles"],"cycle_reduction_fraction":(a["cycles"]-c["cycles"])/a["cycles"],"interpretation":"measured modeled memory-clock/service sensitivity; not physical GPU calibration or causal bandwidth fraction"})
 if sensitivities:row["memory_service_sensitivity"]={"status":"MEASURED_MATCHED_CLOCK_RESPONSE","comparisons":sensitivities,"confidence":"HIGH_EXACT_PAIR_IDENTITY","label":"POSITIVE_MEASURED_RESPONSE" if all(x["cycle_reduction_fraction"]>0 for x in sensitivities) else "MIXED_OR_NONPOSITIVE_RESPONSE"}
# Carry new Source812 Vector endpoint as its own layer; do not overwrite Source78.
current=V/"activation_20261105_v1/control/PERFORMANCE_CURRENT.json";pin(current);v5=load(current)
for point in v5["points"]:
 if point["group"]!="B":continue
 s=load(point["spec_ref"]["path"]);row=next(x for x in rows if x["input_identity_sha256"]==s["input_identity_sha256"])
 row.setdefault("source812_accepted_layers",[]).append({k:point[k] for k in ["cohort","cycles","source_identity","spec_ref","actual_geometry","mode","mechanisms","closed_counter_summary_ref","validation_ref","elapsed_seconds","host_limits"]})
 row["RO_policy_activation"]="MEASURED_NOT_ACTIVATED_VECTOR1700_POLICY1"
 row["source812_interpretation"]="pressure policy saved10500/55925 cycles18.775%; activation0/native-before1M/acceptedRO0; no proof of accelerated active RO, T gain or other input behavior"
# Preserve actual small-geometry detaches in separate layer.
for row in rows:row["separate_small_geometry_detach_evidence"]=[x for x in old["actual_smallG_final_RO_detaches"] if x["input_identity_sha256"]==row["input_identity_sha256"]]
rules={"ordinary_line_MSHR":"Actual saturation iff measured line_full_events_sum>0; peak128 alone is occupancy not denied request. Exact native line capacity128. A zero means none observed in that exact mode/source/config, not universally safe.","descriptor":"actual pressure iff typed descriptor_full_events_sum>0; peak/cap512 kept continuous; no artificial high-pressure threshold","RO_traffic":"accepted_ro>0 marks traffic present; traffic count>=1M and merge_fraction>=0.5 may be described numerically but do not classify activation/profitability","merge":"merges/accepted_RO requester admissions only, undefined when denominator0; not fraction of DRAM traffic removed","Tag_reserved":"UNKNOWN unless actual matching certified timed-head probe/RESERVATION_FAIL observation exists; detach is distinct actual event not occupancy proxy","memory_sensitivity":"only exact matched modeledDRAM850->1020 option perturbation with Source5,input,ordered population,mode,allotheroptions equal; no arbitrary binary cutoff; retain measured fraction","Core812_activation":"timed_frontend && directory_ready && certified_candidate && probe!=HIT && (probe==RESERVATION_FAIL || nativeLineMSHR>=128). Source78 saturation only candidate-selection evidence."}
result={"schema":"UNIFIED_MEMORY_TAXONOMY_AGENT_B_V1","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"population":{"original_rows":103,"ordinary_content_groups":96,"unresolved_slots":7,"representative_inputs":35,"target_programs_or_slots":42},"rules":rules,"rows":rows,"coverage":{"rows_with_reference_endpoints":sum(bool(r["endpoints"]) for r in rows),"source78_reference_endpoints":sum(len(r["endpoints"]) for r in rows),"rows_with_matched_clock_sensitivity":sum(r["memory_service_sensitivity"]["status"]=="MEASURED_MATCHED_CLOCK_RESPONSE" for r in rows),"source812_fullapp_pressure_policy_inputs":1,"new_application_models":0,"budget_consumption":0},"input_refs":list(refs.values()),"boundary":{"no_raw_or_trace_body_scan":True,"no_registry_or_old_artifact_changes":True,"no_EP_speedup_used_as_feature_label":True,"no_waits_added_as_critical_path":True,"no_lower_payload_bytes_called_completed_DRAM_bandwidth":True}}
(O/"MEMORY_RESOURCE_CLASSIFICATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
columns=["original_row_index","program","input_identity_sha256","classification_status","reference_endpoint_count","memory_sensitivity","line_pressure_modes","descriptor_pressure_modes","source812_activation"]
with open(O/"MEMORY_RESOURCE_CLASSIFICATION_COMPACT.csv","w",newline="") as h:
 w=csv.DictWriter(h,fieldnames=columns);w.writeheader()
 for r in rows:w.writerow({"original_row_index":r["original_row_index"],"program":r["program"],"input_identity_sha256":r["input_identity_sha256"],"classification_status":r["classification_status"],"reference_endpoint_count":len(r["endpoints"]),"memory_sensitivity":r["memory_service_sensitivity"]["status"],"line_pressure_modes":";".join(e["mode"] for e in r["endpoints"] if e["labels"]["ordinary_line_MSHR_pressure"]=="ACTUAL_SATURATION_OBSERVED"),"descriptor_pressure_modes":";".join(e["mode"] for e in r["endpoints"] if e["labels"]["descriptor_pressure"]=="ACTUAL_SATURATION_OBSERVED"),"source812_activation":r["RO_policy_activation"]})
print(json.dumps(result["coverage"]))
