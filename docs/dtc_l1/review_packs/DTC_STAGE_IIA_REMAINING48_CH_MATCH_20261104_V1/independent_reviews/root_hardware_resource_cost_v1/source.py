from pathlib import Path
import json,subprocess,hashlib,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');C=Path('/root/data/dtc_failure_repair_20261025_v1/core');COMMIT='9eedb3131937748f0492fa83aad37d3691118d70'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','safe.directory='+str(C),'-C',str(C),*args])
assert git('rev-parse','HEAD').decode().strip()==COMMIT
contract=json.loads((A/'agents/B_runtime_analysis_v1/CORE32_REFERENCE_CONTRACT.json').read_bytes());ch=next(x for x in contract['original128_references']if x['program']=='BlackScholes'and x['source_cell']=='CH'and x['source_profile']=='P0');dh=next(x for x in contract['original128_references']if x['program']=='BlackScholes'and x['source_cell']=='DH'and x['source_profile']=='P0')
for record in [ch,dh]:assert sha(Path(record['source_RESULT_path']).read_bytes())==record['source_RESULT_sha256']
opts=ch['effective_options'];dop=dh['effective_options'];number=lambda k:int(opts[k][0]);assert number('-gpgpu_n_mem')==20 and number('-gpgpu_n_sub_partition_per_mchannel')==2 and number('-gpgpu_dram_return_queue_size')==192
assert opts['-gpgpu_cache:dl2']==['S:128:128:16,L:B:m:L:L,A:192:4,32:0,32']and opts['-dram_seperate_write_queue_enable']==['0']
witnesses=[]
for path,ranges in [('src/gpgpu-sim/l2cache.cc',[(131,175)]),('src/gpgpu-sim/dram.cc',[(113,125),(164,196)]),('src/gpgpu-sim/dram_sched.cc',[(64,88)]),('src/gpgpu-sim/gpu-sim.cc',[(287,300)])]:
 blob=git('show',COMMIT+':'+path);assert blob==(C/path).read_bytes();lines=blob.decode().splitlines()
 witnesses.append(dict(commit=COMMIT,path=str(C/path),relative_path=path,sha256=sha(blob),excerpts=[dict(start=a,end=b,text='\n'.join(str(i)+': '+lines[i-1]for i in range(a,b+1)))for a,b in ranges]))
table=[]
for name,f in [('P0',64),('F128',128),('F256',256)]:
 shared=f+192-(2-1)
 table.append(dict(profile=name,FR_pending_request_limit_per_controller=f,controller_count=20,nominal_FR_entries_all_controllers=20*f,extra_FR_entries_vs_P0=20*(f-64),shared_credit_limit_per_partition=shared,sum_shared_credit_allowance_all_partitions=20*shared,extra_shared_credit_allowance_vs_P0=20*(f-64),return_queue_per_controller=192,separate_write_queue_enabled=False,L2_data_bytes=128*128*16*40,L2_subpartition_count=40,L2_MSHR_entries_per_subpartition=192,L2_MSHR_entries_total=192*40,L2_max_merge_per_entry=4,L2_miss_queue_per_subpartition=32,L2_miss_queue_entries_total=32*40))
out=A/'root_hardware_resource_cost_v1';assert not out.exists();out.mkdir()
data=dict(schema='DTC_STAGEIIA_FIXED_DOWNSTREAM_LOGICAL_RESOURCE_COST_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FIXED_CONFIGURATION_AND_SOURCE_VERIFIED',source_references=witnesses,configuration_sources=[{k:r[k]for k in ['program','input_digest','source_cell','source_profile','source_RESULT_path','source_RESULT_sha256']}for r in [ch,dh]],logical_resources=table,CH_L1_config=opts['-gpgpu_cache:dl1'],DH_L1_compatibility_config=dop['-gpgpu_cache:dl1'],CH_DH_DTC_options_differences={k:[opts.get(k),dop.get(k)]for k in sorted(set(opts)|set(dop))if opts.get(k)!=dop.get(k)},hardware_bytes_not_estimated=True,scientific_limits=['FR queue and shared-credit allowance are coupled by actual Core formula; this is not isolated queue capacity.','Credit is an arbitration accounting allowance, not an extra physical buffer; do not add FR entries and credit counts into independent SRAM storage.','L2 data calculation excludes tag/sector status and other metadata. Nominal MSHR/miss queue capacities do not establish occupancy or actual hardware layout.','Host RSS and C++ queue/list/pointer size do not measure chip SRAM area or energy.','CH/DH L1 data, Tag, physical pool, PIB and timing differ; matching downstream settings does not imply equal area.','This file establishes configuration cost, not performance or a chosen optimal F profile.'],new_models=0,native_writes=0,old_source_changes=0)
(out/'RESOURCE_COST.json').write_text(json.dumps(data,indent=2)+'\n')
text='''# Fixed downstream resource cost

The fixed Core and accepted effective options establish20 DRAM controllers,2 L2 subpartitions per controller and40 identical256KiB L2 banks:10MiB data. L2 MSHR192, merge4 and miss queue32 per bank remain unchanged.

| Profile | FR entries/controller | FR entries total | Extra vsP0 | Shared credits/partition | Extra shared allowance total |
| --- | ---: | ---: | ---: | ---: | ---: |
| P0 | 64 | 1280 | 0 | 255 | 0 |
| F128 | 128 | 2560 | 1280 | 319 | 1280 |
| F256 | 256 | 5120 | 3840 | 447 | 3840 |

The source computes shared limit as `FR + return_queue192 - (subpartitions2 - 1)` with separate write queues disabled. Each subpartition retains its one private credit. Credits are arbitration accounting, not an independent added SRAM queue: the two extra columns must not be summed as separate buffer storage.

These are logical capacity counts. Physical entry encoding, payload/metadata storage, ports, arbitration, delay, area and energy are not modeled by multiplying simulator C++ objects or host RSS. CH conventional96KiB and DH80KiB physical pool plus its compatibility cache/Tag/PIB/completion structures remain unequal. Matching F settings does not imply equal area or free hardware. No performance optimum is claimed and no new run is authorized.
'''
(out/'README.md').write_text(text);(out/'source.py').write_bytes(Path(__file__).read_bytes());files=[dict(path=p.name,sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(out.iterdir())];(out/'MANIFEST.json').write_text(json.dumps(dict(schema='DTC_RESOURCE_COST_MANIFEST_V1',files=files,new_models=0,native_writes=0),indent=2)+'\n');print(json.dumps(dict(path=str(out),manifest_sha256=sha((out/'MANIFEST.json').read_bytes()),status=data['status'])))
