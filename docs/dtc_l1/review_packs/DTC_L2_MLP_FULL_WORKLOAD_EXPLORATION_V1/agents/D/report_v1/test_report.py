"""Scientific arithmetic cases and a closed-source acquisition/render fixture."""
import pathlib,importlib.util,tempfile,json,math,hashlib
H=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('report_fixture',H/'build_report.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=0
def ck(v):
 global checks
 assert v;checks+=1
def near(a,b):ck(a is not None and abs(a-b)<1e-12)
def point(name,cell,profile):return dict(cohort=name+'-'+cell+'-'+profile,input_digest=name*64,program=name,suite='suite1'if name in['a','b']else'suite2',profile=profile,cell=cell)
points=[];records={}
for name in['a','b','c']:
 for profile in['P0','E384','F128']:
  for cell in['CH','DH']:
   p=point(name,cell,profile);points.append(p)
def add(name,cell,profile,cycles,state=None):
 c=point(name,cell,profile)['cohort'];records[c]=dict(state=state or m.PASS,cycles=cycles,proof=dict(cycles=cycles,performance_accepted=True),archive={'verified':True})
for name,ch0,dh0,chv,dhv in[('a',100,200,40,100),('b',400,100,800,200)]:
 for cell,profile,cyc in[('CH','P0',ch0),('DH','P0',dh0),('CH','E384',chv),('DH','E384',dhv)]:add(name,cell,profile,cyc)
add('a','DH','F128',200)
# c has a variant but no accepted baseline; positive numeric failure is excluded.
add('c','DH','E384',1);add('c','DH','P0',999,'FAIL_L2MLP_ARCHIVED_NO_RETRY');add('b','DH','F128',999,'FAIL_L2MLP_ARCHIVED_NO_RETRY')
matrix=dict(points=points,unresolved_programs=7,revision=0)
r=m.analyze(matrix,records,batch=dict(running=['c-CH-P0'],postprocess=['c-CH-F128']))
s=r['statistics']['E384']['ALL'];near(s['DH_speedup']['GM'],1);near(s['DH_speedup']['median'],1.25);near(s['CH_speedup']['GM'],math.sqrt(1.25));near(s['relative_DTC_improvement']['GM'],math.sqrt(.8));near(s['CH_over_DH']['GM'],math.sqrt(1.6))
ck(s['DH_speedup']['n']==2);ck(s['DH_speedup']['expected_n']==3);ck(s['DH_speedup']['missing_n']==1);ck(s['DH_speedup']['positive']==1);ck(s['DH_speedup']['negative']==1);ck(s['DH_speedup']['neutral']==0)
ck(r['table']['c'*64]['P0']['DH']['cycles']is None);ck(r['table']['c'*64]['P0']['DH']['raw_reported_cycles']==999);ck(r['table']['c'*64]['P0']['CH']['state']=='RUNNING_UNVERIFIED');ck(r['table']['c'*64]['F128']['CH']['state']=='POSTPROCESS_UNVERIFIED')
ck(r['comparisons']['c'*64]['E384']['DH_speedup']is None);ck(r['statistics']['F128']['ALL']['CH_speedup']['n']==0);ck(r['statistics']['F128']['ALL']['relative_DTC_improvement']['GM']is None)
common=r['fixed_all_profile_common_population']['ALL']['DH_speedup'];ck(common['population']==['a'*64]);near(common['by_profile']['E384']['GM'],2);near(common['by_profile']['F128']['GM'],1);ck(r['fixed_all_profile_common_population']['ALL']['relative_DTC_improvement']['n']==0)
ck(r['statistics']['E384']['suite2']['DH_speedup']['GM']is None);ck(r['statistics']['E384']['suite2']['DH_speedup']['missing_n']==1)
# Reference acceptance requires all proofs; a failing reference cannot join GM.
ref=dict(state=m.REF,cycles=10,proof=dict(performance_accepted=True,cycles=10),reuse_verification={k:True for k in m.REUSE_PROOFS});ck(m.accepted(ref))
for k in m.REUSE_PROOFS:
 bad=json.loads(json.dumps(ref));bad['reuse_verification'][k]=False;ck(not m.accepted(bad))
ck(m.counter_projection({})['L2_read_miss_sectors']is None)
ck(m.counter_projection(dict(traffic=dict(L2_buckets={'GLOBAL_ACC_R:MISS':0,'GLOBAL_ACC_R:SECTOR_MISS':0})))['L2_read_miss_sectors']==0)
records['a-DH-E384']['proof']['traffic']=dict(L2_accepted_read_32B_sectors=10,L2_buckets={'GLOBAL_ACC_R:MISS':2,'GLOBAL_ACC_R:SECTOR_MISS':0})
single=m.analyze(matrix,records,stream_scopes={'a'*64:dict(L2_last_printed_scope='SINGLE_STREAM_DECLARED_TRACE_TOTAL')});ck(single['table']['a'*64]['E384']['DH']['counters']['L2_read_sectors']==10)
multi=m.analyze(matrix,records,stream_scopes={'a'*64:dict(L2_last_printed_scope='MULTISTREAM_REQUIRES_PER_STREAM_LAST_SNAPSHOT_AGGREGATION')});cc=multi['table']['a'*64]['E384']['DH']['counters'];ck(cc['L2_read_sectors']is None);ck(cc['raw_last_printed_stream_L2_read_sectors']==10);ck(cc['L2_read_miss_sectors']is None)
def stat(pid=123,start=777,state='R'):
 return (str(pid)+' (model with embedded ) parentheses) '+' '.join([state]+['0']*18+[str(start)]+['0']*30)).encode()
proof=dict(pid=123,start_ticks=777,cmdline='/loader /model -config /cfg ',mnt_namespace='mnt:[1]',exe='/loader')
def live(before=None,after=None,cmd=b'/loader\x00/model\x00-config\x00/cfg\x00',mnt='mnt:[1]',exe='/loader'):
 return m.process_identity_matches(proof,before or stat(),cmd,after or stat(),mnt,exe)
ck(live());ck(not live(before=stat(start=778)));ck(not live(after=stat(start=778)));ck(not live(after=stat(state='Z')));ck(not live(before=stat(state='X')));ck(not live(cmd=b'/unrelated\x00'));ck(not live(mnt='mnt:[2]'));ck(not live(exe='/unrelated'));ck(not live(before=stat(pid=124)))
confirmed=m.analyze(matrix,records,liveness={'c-CH-P0':dict(status='RUNNING_CONFIRMED',pid=123,start_ticks=777)})
ck(confirmed['table']['c'*64]['P0']['CH']['state']=='RUNNING_CONFIRMED');ck(confirmed['state_counts']['RUNNING_CONFIRMED']==1)
with tempfile.TemporaryDirectory()as td:
 root=pathlib.Path(td);cohort='fixture';sources={};ip=root/'control/qualification_ledger/fixture.INTENT.json';ip.parent.mkdir(parents=True);out=root/'DTC/run/results/uuid';out.mkdir(parents=True)
 ck(m.live_identity(root,cohort,sources)['status']=='ADMISSION_OR_START_AWAITING_IDENTITY')
 ip.write_bytes(m.encode(dict(cohort=cohort,uuid='uuid',output=str(out))))
 ck(m.live_identity(root,cohort,sources)['status']=='SPENT_AWAITING_PID_PROOF')
 dp=ip.with_name('fixture.DONE.json');dp.write_bytes(m.encode(dict(uuid='uuid')))
 ck(m.live_identity(root,cohort,sources)['status']=='TERMINAL_AWAITING_STRICT_ARCHIVE')
 dp.write_bytes(m.encode(dict(uuid='wrong')));ck(m.live_identity(root,cohort,sources)['status']=='SPENT_LIVENESS_UNVERIFIED_AWAITING_TERMINAL');dp.unlink()
 ex=out/'NATIVE_EXIT.json';ex.write_bytes(m.encode(dict(uuid='uuid')));ck(m.live_identity(root,cohort,sources)['status']=='EXIT_OBSERVED_AWAITING_DONE')
 ex.write_bytes(m.encode(dict(uuid='wrong')));ck(m.live_identity(root,cohort,sources)['status']=='SPENT_LIVENESS_UNVERIFIED_AWAITING_TERMINAL')
spec=dict(expected_options={'-gpgpu_cache:dl2':['S:128:128:16,L:B:m:L:L,A:384:4,32:0,32'],'-gpgpu_n_mem':['20'],'-gpgpu_n_mem_per_ctrlr':['1'],'-gpgpu_n_sub_partition_per_mchannel':['2'],'-gpgpu_frfcfs_dram_sched_queue_size':['64'],'-gpgpu_clock_domains':['1410.0:1410.0:1410.0:850.0']})
p=m.parameters(spec);ck(p['L2_total_capacity_bytes']==10*1024**2);ck(p['total_L2_MSHR_entries']==15360);ck(p['total_MSHR_merge_slots_upper_bound']==61440);ck(p['total_L2_miss_queue_slots']==1280);ck(p['total_FRFCFS_queue_slots']==1280);near(p['dram_MHz'],850)
with tempfile.TemporaryDirectory()as td:
 root=pathlib.Path(td)/'live';out=pathlib.Path(td)/'derived'
 def write(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(m.encode(obj))
 base=root/'control/SCOPE.json';write(base,matrix);current=dict(matrix,base_scope_sha256=hashlib.sha256(base.read_bytes()).hexdigest());write(root/'control/MATRIX_CURRENT.json',current)
 for point in points:
  c=point['cohort'];write(root/'control/specs'/(c+'.json'),spec)
  if c in records:
   v=json.loads(json.dumps(records[c]));v['proof']['effective_options']=spec['expected_options'];write(root/'analysis'/(c+'.RESULT.json'),v)
 fake_summary=dict(utc='fixture',aggregates={f:{'ALL':r['statistics'][f]['ALL']}for f in r['profiles']});write(root/'analysis/AUTO_SUMMARY.json',fake_summary)
 actual=m.acquire(root,'FIXTURE_COMMIT');ck(len(actual['source_snapshots'])>10);ck(not actual['uniform_option_errors']);ck(all(q['GM_match_on_same_population']is True for q in actual['summary_crosschecks']));ck(actual['partial'])
 manifest=m.write_report(actual,out)
 for n in['dashboard.html','report.json','sensitivity.png','sensitivity.svg','REPORT_MANIFEST.json']:ck((out/n).stat().st_size>0)
 ck('a'*64 in(out/'dashboard.html').read_text());ck('FAIL_L2MLP_ARCHIVED_NO_RETRY'in(out/'dashboard.html').read_text());ck('PARTIAL'in(out/'dashboard.html').read_text());ck('FIXTURE_COMMIT'in(out/'dashboard.html').read_text())
 # Empty coverage must render an explicit pending chart, not a zero-speedup plot.
 empty=m.analyze(matrix,{});empty.update(utc='fixture',existing_summary_utc=None,generator=dict(sha256='fixture',tool_commit='fixture'),root=str(root),source_snapshots=[],uniform_option_errors=[],summary_crosschecks=[],snapshot_note='empty coverage fixture')
 m.write_report(empty,out/'empty');ck('PENDING: no valid matched pairs'in(out/'empty/sensitivity.svg').read_text())
print(json.dumps(dict(status='CPU_ONLY_PASS',checks=checks,actual_simulator_starts=0,analytical_cases=['geometric mean versus arithmetic median','same-design missing denominator','failed positive cycles excluded','negative speedup retained','common fixed-profile intersection','suite denominator missing count','six-proof P0 reuse','missing versus genuine zero counter','structure counts not area','closed source acquisition and SHA','render pending empty chart'],generator_sha256=hashlib.sha256((H/'build_report.py').read_bytes()).hexdigest()),indent=2))
