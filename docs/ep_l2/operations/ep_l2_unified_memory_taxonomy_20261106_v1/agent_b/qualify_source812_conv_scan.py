from pathlib import Path
import json,hashlib,subprocess,time,os,resource,datetime
B=Path("/root/data/ep_l2_full_workload_performance_20261027_v1")
O=B/"research/unified_memory_taxonomy_20261106_v1/agent_b"
V=B/"research/performance_first_v5_20261105_v1/track_b_fullf"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {"path":str(p),"bytes":Path(p).stat().st_size,"sha256":sha(p)}
def run(a,tag,timeout=60):
 t=time.monotonic()
 with open(O/(tag+".stdout"),"wb") as so,open(O/(tag+".stderr"),"wb") as se:
  x=subprocess.run(a,stdout=so,stderr=se,cwd=O,timeout=timeout)
 return {"argv":a,"returncode":x.returncode,"seconds":time.monotonic()-t,"stdout_ref":ref(O/(tag+".stdout")),"stderr_ref":ref(O/(tag+".stderr"))}
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
source= B/"agent_a/ro_qualification/test_actual_ro_loader_generic.cc"
s=source.read_text().replace("assert(argc==8);","assert(argc==9);").replace("loader_config cfg(v);","loader_config cfg(v);cfg.m_ro_pressure_epoch_for_test_placeholder;")
# policy assignment is inside public derived constructor, and argc=9 carries argv8 policy.
s=s.replace("loader_config cfg(v);cfg.m_ro_pressure_epoch_for_test_placeholder;","loader_config cfg(v);")
s=s.replace("m_ro_tag_detach=true;m_ro_line_mshr_bypass=true;","m_ro_tag_detach=true;m_ro_line_mshr_bypass=true;m_ro_pressure_epoch=std::stoul(v[8]);")
s=s.replace('RO_LOADER_PRODUCTION|','SOURCE812_RO_LOADER_PRODUCTION|')
target=O/"test_source812_generic_ro_loader.cc";target.write_text(s)
build=json.load(open(V/"cpu/BUILD.json"))["argv"]
build=[str(target) if x.endswith("/cpu/test_pressure_epoch.cc") else str(O/"source812_generic_ro_loader") if x.endswith("/cpu/pressure_epoch_cpu") else x for x in build]
pins={x:sha(x) for x in build if x.endswith(".a")}
identity=json.load(open(V/"NEW_SOURCE5.json"))["source_identity"]
assert pins[str(V/"build/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a")]==identity["archive_sha256"]
receipt={"schema":"TAXONOMY_B_SOURCE812_EXACT_CONV_SCAN_CPU_REBIND_V1","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"new_application_starts":0,"budget_consumption":0,"source_identity":identity,"original_fixture_source_ref":ref(source),"fixture_source_ref":ref(target),"linked_library_pins":pins,"compile":run(build,"compile",120),"input_checks":[]}
assert receipt["compile"]["returncode"]==0
features=json.load(open(B/"research/observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json"))
for row in features["rows"]:
 if row["program"] not in ["convolutionSeparable","scan"]:continue
 e=next(x for x in row["reference_endpoints"] if x["mode"]=="F");spec=json.load(open(e["spec_ref"]["path"]))
 q=json.load(open(spec["ro_qualification_ref"]["path"]));binding=json.load(open(spec["input_binding_ref"]["path"]))
 p=Path(spec["trace_entry"]);command=p.read_bytes();assert hashlib.sha256(command).hexdigest()==binding["literal_commandlist_sha256"]
 manifest=json.load(open(q["manifest_ref"]["path"]));assert manifest["commandlist_sha256"]==hashlib.sha256(command).hexdigest()
 assert [x.strip() for x in command.decode().splitlines() if x.strip()]==binding["expectedcommands"]
 for rr in [e["spec_ref"],spec["input_binding_ref"],spec["ro_qualification_ref"],q["manifest_ref"],q["ranges_ref"]]+spec["ordered_configs"]:assert sha(rr["path"])==rr["sha256"],rr["path"]
 ranges=Path(q["ranges_ref"]["path"]).read_text().splitlines()[1:]
 count=sum((int(x.split(",")[1],16)-int(x.split(",")[0],16))//128+1 for x in ranges if x.strip())
 check={"program":row["program"],"input_identity_sha256":row["input_identity_sha256"],"old_source_spec_ref":e["spec_ref"],"input_binding_ref":spec["input_binding_ref"],"ordered_commandlist_ref":ref(p),"kernel_body_hashes_reused_not_reread":binding["ordered_kernel_identity"],"ro_manifest_ref":q["manifest_ref"],"ro_ranges_ref":q["ranges_ref"],"RO_loader_runs":[],"parser_runs":[]}
 for policy in [0,1]:
  args=[str(O/"source812_generic_ro_loader"),q["manifest_ref"]["path"],q["manifest_ref"]["sha256"],q["ranges_ref"]["path"],q["ranges_ref"]["sha256"],q["scope"],str(p),str(count),str(policy)]
  r=run(args,row["program"]+"_loader_"+str(policy));assert r["returncode"]==0
  assert "SOURCE812_RO_LOADER_PRODUCTION|" in Path(r["stdout_ref"]["path"]).read_text()
  check["RO_loader_runs"].append(r)
  delta=O/(row["program"]+"_policy"+str(policy)+".config");delta.write_text("-gpgpu_ep_l2_ro_pressure_epoch "+str(policy)+"\n")
  args=[str(V/"cpu/full_option_echo")]
  for rr in spec["ordered_configs"]:args+=["-config",rr["path"]]
  args+=["-config",str(delta),"-trace",str(p)]
  r=run(args,row["program"]+"_parser_"+str(policy));assert r["returncode"]==0
  actual={}
  for line in Path(r["stdout_ref"]["path"]).read_text().splitlines():
   if line.startswith("-"):
    a=line.split("#",1)[0].split()
    if len(a)>=1:
     k=a[0];v=" ".join(a[1:]);assert k not in actual or actual[k]==v;actual[k]=v
  assert len(actual)==283,len(actual)
  expected=spec["expected_effective_options"]
  assert isinstance(expected,dict)
  mismatches={k:{"expected":str(v),"actual":actual.get(k)} for k,v in expected.items() if actual.get(k)!=str(v)}
  assert not mismatches,mismatches
  assert actual["-gpgpu_ep_l2_ro_pressure_epoch"]==str(policy)
  r.update({"unique_keys":len(actual),"old282_exact_preserved":True,"policy":policy,"delta_ref":ref(delta),"effective_options":actual})
  check["parser_runs"].append(r)
 check["status"]="EXACT_COMMANDLIST_METADATA_AND_SOURCE812_PRODUCTION_RO_LOADER_BOTH_POLICIES_AND_283_PARSER_CPU_PASS"
 check["limits"]=["Not an application launch grant or full-application qualification","Kernel body hashes reused from accepted frozen input; no trace body scan","No epoch/request/cycle/GPU object in loader; pressure reachability reused from prior production CPU tests","New per-input source-qualified Spec/43-field Host/Native22+Host5 binding and resource admission remain Main preactivation work","Full-application pressure activation and performance remain UNKNOWN"]
 receipt["input_checks"].append(check)
for p,h in pins.items():assert sha(p)==h
receipt["binary_ref"]=ref(O/"source812_generic_ro_loader")
receipt["parser_ref"]=ref(V/"cpu/full_option_echo")
receipt["status"]="FINITE_NEW_INPUT_CPU_REBIND_PASS_NO_SCIENCE_AUTHORITY"
(O/"SOURCE812_CONV_SCAN_CPU_QUALIFICATION.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps({"status":receipt["status"],"input_checks":len(receipt["input_checks"]),"compile_s":receipt["compile"]["seconds"],"runs":sum(len(x["RO_loader_runs"])+len(x["parser_runs"]) for x in receipt["input_checks"])}))
