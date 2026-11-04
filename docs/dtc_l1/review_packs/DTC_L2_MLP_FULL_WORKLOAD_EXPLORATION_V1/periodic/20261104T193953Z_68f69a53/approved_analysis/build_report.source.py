"""Read-only incremental L2-MLP report. One invocation, no daemon or dispatch.

python3 build_report.py --root /root/data/dtc_l2_mlp_exploration_20261027_v1 --output DIR
Every consumed JSON is read once from a stable file descriptor and SHA-labelled.
Only this report's output directory is writable. No production modules imported.
"""
import argparse,collections,datetime,hashlib,html,json,math,os,pathlib,re,statistics,sys
P=pathlib.Path
_deps=P(__file__).resolve().parent/('.windows-deps'if os.name=='nt'else'.python-deps')
if _deps.exists():sys.path.insert(0,str(_deps))
PASS='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE';REF='REFERENCE_ACCEPTED_NO_NEW_START'
METRICS=('DH_speedup','CH_speedup','relative_DTC_improvement','CH_over_DH')
REUSE_PROOFS=('strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal')

def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def source(p,sources):
 """Read a coherent inode, not multiple path opens across atomic replacement."""
 for attempt in range(3):
  with P(p).open('rb')as h:
   before=os.fstat(h.fileno());b=h.read();after=os.fstat(h.fileno())
  if (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)and len(b)==after.st_size:break
 else:raise RuntimeError('Source changed during non-atomic write: '+str(p))
 v=json.loads(b);sources[str(p)]=dict(path=str(p),sha256=sha(b),bytes=len(b),inode=after.st_ino,mtime_ns=after.st_mtime_ns)
 return v

def accepted(v):
 pr=v.get('proof',{});c=v.get('cycles')
 if type(c)is not int or c<=0 or pr.get('performance_accepted')is not True or pr.get('cycles')!=c:return False
 if v.get('state')==PASS:return bool(v.get('archive'))
 if v.get('state')==REF:return all(v.get('reuse_verification',{}).get(k)is True for k in REUSE_PROOFS)
 return False

def aggregate(values,expected):
 """values maps stable full input SHA to a positive, paired ratio."""
 a=list(values.values());assert all(math.isfinite(v)and v>0 for v in a)
 return dict(n=len(a),expected_n=expected,missing_n=expected-len(a),coverage=len(a)/expected if expected else None,GM=math.exp(math.fsum(math.log(v)for v in a)/len(a))if a else None,median=statistics.median(a)if a else None,positive=sum(v>1 for v in a),neutral=sum(v==1 for v in a),negative=sum(v<1 for v in a),minimum=min(a)if a else None,maximum=max(a)if a else None,population=sorted(values),values=values)

def counter_projection(pr):
 t=pr.get('traffic',{});m=pr.get('metrics',{});b=t.get('L2_buckets',{})
 misses=[n for k,n in b.items()if k.partition(':')[0].endswith('_R')and k.partition(':')[2]in('MISS','SECTOR_MISS')]
 return dict(L2_read_sectors=t.get('L2_accepted_read_32B_sectors'),L2_read_miss_sectors=sum(misses)if misses else None,DRAM_read_atoms=t.get('DRAM_issued_read_atoms'),DRAM_read_bytes=t.get('DRAM_read_payload_bytes'),L2_reservation_fail=m.get('L2_total_cache_reservation_fails'),gpu_stall_dramfull=m.get('gpu_stall_dramfull'),L2_specific_MSHR_reasons={k:v for k,v in m.items()if'l2'in k.lower()and'mshr'in k.lower()}or None,avg_mrq_latency_last_printed=pr.get('latency_counters',{}).get('avg_mrq_latency'))

def parameters(spec):
 o=spec['expected_options'];dl=o['-gpgpu_cache:dl2'];assert len(dl)==1
 fields=dl[0].split(',');geom=fields[0].split(':');mshr=fields[2].split(':');miss=fields[3].split(':')
 sets,line,ways=map(int,geom[1:]);entries,merge=map(int,mshr[1:]);queue=int(miss[0])
 controllers=int(o['-gpgpu_n_mem'][0])*int(o.get('-gpgpu_n_mem_per_ctrlr',['1'])[0]);sub=int(o['-gpgpu_n_sub_partition_per_mchannel'][0]);parts=controllers*sub
 fr=int(o['-gpgpu_frfcfs_dram_sched_queue_size'][0]);clock=o['-gpgpu_clock_domains'][0]
 return dict(L2_raw_option=dl[0],clock_domains=clock,dram_MHz=float(clock.split(':')[-1]),sets=sets,line_bytes=line,ways=ways,L2_subpartitions=parts,DRAM_controllers=controllers,L2_total_capacity_bytes=sets*line*ways*parts,MSHR_entries_per_subpartition=entries,max_merge_per_MSHR_entry=merge,miss_queue_per_subpartition=queue,FRFCFS_queue_per_controller=fr,total_L2_MSHR_entries=entries*parts,total_MSHR_merge_slots_upper_bound=entries*merge*parts,total_L2_miss_queue_slots=queue*parts,total_FRFCFS_queue_slots=fr*controllers,notes='Structural counts, not area/bit costs. Merge slots are a limit product, not measured occupancy. FRFCFS queue changes memory-partition credit coupling.')

def process_identity_matches(proof,stat_before,cmdline,stat_after,mnt_namespace,exe):
 """Double-read /proc start ticks protects against PID reuse during acquisition."""
 def parse(b):
  text=b.decode();head,tail=text.rsplit(')',1);fields=tail.split()
  return int(head.split('(',1)[0].strip()),fields[0],int(fields[19])
 first=parse(stat_before);last=parse(stat_after)
 observed=' '.join(x.decode()for x in cmdline.split(b'\x00')if x).strip()
 return (first[0]==last[0]==proof['pid'] and first[2]==last[2]==proof['start_ticks'] and first[1]not in['Z','X','x']and last[1]not in['Z','X','x']and observed==proof['cmdline'].strip()and mnt_namespace==proof['mnt_namespace']and exe==proof['exe'])

def live_identity(root,c,sources):
 """Controller membership alone never implies a live model."""
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json')
 v=dict(cohort=c,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='ADMISSION_OR_START_AWAITING_IDENTITY')
 try:
  if not ip.exists():return v
  intent=source(ip,sources);v.update(uuid=intent['uuid'],intent_path=str(ip),intent_sha256=sources[str(ip)]['sha256'])
  assert intent['cohort']==c and P(intent['output'])==root/'DTC/run/results'/intent['uuid']
  out=P(intent['output']);v['status']='SPENT_AWAITING_PID_PROOF'
  if dp.exists():
   done=source(dp,sources);assert done['uuid']==intent['uuid'];v.update(status='TERMINAL_AWAITING_STRICT_ARCHIVE',done_uuid=done.get('uuid'));return v
  exitpath=out/'NATIVE_EXIT.json'
  if exitpath.exists():
   exitproof=source(exitpath,sources);assert exitproof['uuid']==intent['uuid'];v.update(status='EXIT_OBSERVED_AWAITING_DONE',exit_uuid=exitproof.get('uuid'));return v
  pp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if not pp.exists():return v
  proof=source(pp,sources);v.update(pid=proof['pid'],start_ticks=proof['start_ticks'],pid_proof_path=str(pp),pid_proof_sha256=sources[str(pp)]['sha256'])
  assert proof['dispatch_binding_sha256']==intent['dispatch_binding_sha256']and proof['l2_mlp_execution_binding']==intent['l2_mlp_execution_binding']
  proc=P('/proc')/str(proof['pid']);before=(proc/'stat').read_bytes();cmdline=(proc/'cmdline').read_bytes();mnt=os.readlink(proc/'ns/mnt');exe=os.readlink(proc/'exe');after=(proc/'stat').read_bytes()
  ok=process_identity_matches(proof,before,cmdline,after,mnt,exe)
  v.update(status='RUNNING_CONFIRMED'if ok else'SPENT_PID_IDENTITY_MISMATCH_AWAITING_TERMINAL',proc_identity_matches=ok,stat_before_sha256=sha(before),stat_after_sha256=sha(after),cmdline_sha256=sha(cmdline),observed_mnt_namespace=mnt,observed_exe=exe)
 except (OSError,ValueError,KeyError,AssertionError)as e:
  v.update(status='SPENT_LIVENESS_UNVERIFIED_AWAITING_TERMINAL'if'uuid'in v else'ADMISSION_OR_START_IDENTITY_UNVERIFIED',observation_error=repr(e))
 return v

def analyze(matrix,records,batch=None,profile_parameters=None,stream_scopes=None,liveness=None):
 """Independent paired arithmetic; no runtime or historical result substitution."""
 batch=batch or{};stream_scopes=stream_scopes or{};liveness=liveness or{};points=matrix['points'];programs={};table={};profiles=[];cohorts=set()
 running=set(batch.get('running',[]));post=set(batch.get('postprocess',[]));errors=batch.get('errors',{})
 for p in points:
  d=p['input_digest'];c=p['cohort'];f=p['profile'];cell=p['cell'];assert cell in('CH','DH')and c not in cohorts;cohorts.add(c)
  if f not in profiles:profiles.append(f)
  info=dict(program=p['program'],suite=p.get('suite','UNKNOWN'),input_digest=d)
  if d in programs:assert programs[d]==info
  else:programs[d]=info
  row=table.setdefault(d,{}).setdefault(f,{})
  assert cell not in row
  v=records.get(c,{});valid=accepted(v)
  state=v.get('state',liveness.get(c,{}).get('status','POSTPROCESS_UNVERIFIED'if c in post else'RUNNING_UNVERIFIED'if c in running else'ENGINEERING'if c in errors else'PENDING'))
  row[cell]=dict(cohort=c,state=state,accepted=valid,cycles=v.get('cycles')if valid else None,raw_reported_cycles=v.get('cycles'),uuid=v.get('uuid',liveness.get(c,{}).get('uuid')),live_identity=liveness.get(c),result_path=v.get('_result_path'),result_sha256=v.get('_result_sha256'),counters=counter_projection(v.get('proof',{}))if valid else None,core_commit=v.get('proof',{}).get('core_commit'),framework_commit=v.get('proof',{}).get('framework_commit'),binary_sha256=v.get('proof',{}).get('binary_sha256'))
  if valid:
   counter=row[cell]['counters'];counter['L2_counter_scope']=stream_scopes.get(d,{}).get('L2_last_printed_scope','UNVERIFIED_STREAM_SCOPE')
   if counter['L2_counter_scope']!='SINGLE_STREAM_DECLARED_TRACE_TOTAL':
    for k in['L2_read_sectors','L2_read_miss_sectors','L2_reservation_fail']:
     counter['raw_last_printed_stream_'+k]=counter[k];counter[k]=None
 def cyc(d,f,c):return table.get(d,{}).get(f,{}).get(c,{}).get('cycles')
 comparisons={}
 for d in programs:
  comparisons[d]={}
  for f in profiles:
   ch0,dh0,ch,dh=cyc(d,'P0','CH'),cyc(d,'P0','DH'),cyc(d,f,'CH'),cyc(d,f,'DH')
   sch=ch0/ch if ch0 and ch else None;sdh=dh0/dh if dh0 and dh else None
   comparisons[d][f]=dict(DH_speedup=sdh,CH_speedup=sch,relative_DTC_improvement=sdh/sch if sdh and sch else None,CH_over_DH=ch/dh if ch and dh else None,matched_quad=bool(ch0 and dh0 and ch and dh))
 suites=sorted({p['suite']for p in programs.values()});stats={};variants=[f for f in profiles if f!='P0']
 for f in profiles:
  stats[f]={}
  for group in['ALL']+suites:
   ids=[d for d,p in programs.items()if group=='ALL'or p['suite']==group];n=len(ids)
   one={k:aggregate({d:comparisons[d][f][k]for d in ids if comparisons[d][f][k]is not None},n)for k in METRICS}
   quad=[d for d in ids if comparisons[d][f]['matched_quad']]
   one['common_matched_quad']={k:aggregate({d:comparisons[d][f][k]for d in quad},n)for k in METRICS}
   stats[f][group]=one
 common={}
 for group in['ALL']+suites:
  ids=[d for d,p in programs.items()if group=='ALL'or p['suite']==group];n=len(ids);common[group]={}
  for k in METRICS:
   ds=[d for d in ids if variants and all(comparisons[d][f][k]is not None for f in variants)]
   common[group][k]=dict(fixed_profiles=variants,population=ds,n=len(ds),expected_n=n,by_profile={f:aggregate({d:comparisons[d][f][k]for d in ds},n)for f in variants})
 state_counts=collections.Counter(x['state']for ps in table.values()for row in ps.values()for x in row.values())
 return dict(schema='DTC_L2_MLP_READONLY_REPORT_V1',matrix_revision=matrix.get('revision',0),frozen_inputs=len(programs),final_target_programs=42,unresolved=matrix.get('unresolved_programs',7),planned_cells=len(points),profiles=profiles,programs=programs,table=table,comparisons=comparisons,statistics=stats,fixed_all_profile_common_population=common,state_counts=dict(state_counts),profile_parameters=profile_parameters or{},stream_scopes=stream_scopes,batch=batch,partial=any(not x['accepted']for ps in table.values()for row in ps.values()for x in row.values()),scientific_rules=dict(P0_denominator='Same design, same input, accepted P0 only',relative_improvement='(DH_P0/DH_variant)/(CH_P0/CH_variant)',CH_over_DH='CH_variant_cycles/DH_variant_cycles',missing='null, never zero',uniform_configuration='Each GM uses one fixed profile; no per-program best selection',GM_populations='Per-metric paired; per-profile common quad; fixed ALL profiles common intersection separately',whole_application_numerical_values='UNPROVEN',DRAM_MHz=850,frozen_architecture='No DTC architecture, L2 capacity or clock changes',latency='Last printed average is not a weighted whole-application statistic',FRFCFS='Queue-size changes memory-partition credit coupling; not isolated L2 capacity',L2_counters='Last-printed L2 buckets are per-stream cumulative. Whole-declared-trace L2 counters shown only with complete single-stream header evidence; otherwise null with raw per-stream values retained. DRAM counters are global cumulative.'))

def acquire(root,tool_commit):
 root=P(root);sources={};base=source(root/'control/SCOPE.json',sources);mp=root/'control/MATRIX_CURRENT.json';matrix=source(mp,sources)if mp.exists()else base
 if mp.exists():
  assert matrix['base_scope_sha256']==sources[str(root/'control/SCOPE.json')]['sha256']
  current={p['cohort']:p for p in matrix['points']};assert len(current)==len(matrix['points'])
  for p in base['points']:assert current.get(p['cohort'])==p
 sp=root/'analysis/AUTO_SUMMARY.json';summary=source(sp,sources)if sp.exists()else None
 bp=root/'analysis/BATCH_STATE.json';batch=source(bp,sources)if bp.exists()else{}
 records={};profile_parameters={};reference_options={};option_errors=[];liveness={}
 active=set(batch.get('running',[]))|set(batch.get('postprocess',[]))
 ledger=root/'control/qualification_ledger';active|={p.name[:-len('.INTENT.json')]for p in ledger.glob('*.INTENT.json')}
 for p in matrix['points']:
  c=p['cohort'];rp=root/'analysis'/(c+'.RESULT.json')
  if rp.exists():
   v=source(rp,sources);v['_result_path']=str(rp);v['_result_sha256']=sources[str(rp)]['sha256'];records[c]=v
  elif c in active:liveness[c]=live_identity(root,c,sources)
  f=p['profile']
  if f not in profile_parameters:
   specpath=root/'control/specs'/(c+'.json')
   if specpath.exists():
    spec=source(specpath,sources);profile_parameters[f]=dict(parameters(spec),source_spec_path=str(specpath),source_spec_sha256=sources[str(specpath)]['sha256']);reference_options[f]=spec['expected_options']
  if c in records and accepted(records[c])and f in profile_parameters:
   # Target L2/FRFCFS/clock fields must be uniform even across CH/DH.
   o=records[c]['proof']['effective_options'];ref=reference_options[f]
   for k in['-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size','-gpgpu_clock_domains']:
    if o.get(k)!=ref.get(k):option_errors.append(dict(cohort=c,option=k,observed=o.get(k),expected=ref.get(k)))
 streamfile=P(__file__).resolve().parent/'input_stream_scope.json';stream_scopes={}
 if streamfile.exists():
  evidence=source(streamfile,sources)
  stream_scopes={r['input_digest']:{k:v for k,v in r.items()if k!='headers'}for r in evidence['rows']}
 result=analyze(matrix,records,batch,profile_parameters,stream_scopes,liveness)
 checks=[]
 if summary:
  for f in result['profiles']:
   for k in METRICS:
    original=summary.get('aggregates',{}).get(f,{}).get('ALL',{}).get(k,{})
    independent=result['statistics'][f]['ALL'][k]
    same=set(original.get('population',[]))==set(independent['population'])
    checks.append(dict(profile=f,metric=k,population_same=same,GM_match_on_same_population=(math.isclose(original['GM'],independent['GM'],rel_tol=1e-12)if same and original.get('GM')is not None and independent['GM']is not None else original.get('GM')is independent['GM']if same else None),old_n=original.get('n'),independent_n=independent['n']))
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();result.update(utc=now,root=str(root),generator=dict(path=str(P(__file__).resolve()),sha256=sha(P(__file__).read_bytes()),tool_commit=tool_commit),source_snapshots=list(sources.values()),existing_summary_utc=summary.get('utc')if summary else None,summary_crosschecks=checks,snapshot_note='Inputs are coherent individual file snapshots, not a transaction spanning controller and all results. New completions can occur during collection.',uniform_option_errors=option_errors)
 return result

def nfmt(v):return '—'if v is None else f'{v:,.0f}'
def rfmt(v):return '—'if v is None else f'{v:.4f}'
def esc(v):return html.escape(str(v))

def html_report(r):
 b=r['batch'];out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DTC L2 MLP report</title><style>body{font:14px system-ui,sans-serif;color:#182333;margin:22px;background:#f8fafc}h1{font-size:24px}p{max-width:1150px;line-height:1.5}.tag{display:inline-block;background:#fff0cb;padding:5px 10px;border-radius:6px}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:white;padding:12px 18px;border:1px solid #d9e1ec;border-radius:8px}table{border-collapse:collapse;background:white;width:100%;font-variant-numeric:tabular-nums}th,td{border:1px solid #e1e7ef;padding:6px 8px;text-align:right;white-space:nowrap}th{background:#edf2f8;position:sticky;top:0}td:first-child,th:first-child,td:nth-child(2){text-align:left}td small{display:block;color:#617086;font-size:10px}.wrap{overflow:auto;max-height:74vh}.good{color:#006b4c}.bad{color:#ac2634}.muted{color:#6f7b8b}code{font-size:11px;overflow-wrap:anywhere}input,select{padding:8px;margin:5px}details{margin:12px 0}a{color:#205dae}.sources td{white-space:normal;text-align:left}img{max-width:1100px;width:100%}</style><h1>DTC L2 concurrency exploration</h1>',f'<span class="tag">{"PARTIAL / 正在执行"if r["partial"]else"All planned cells accepted"}</span><p>Snapshot UTC {esc(r["utc"])} · source summary UTC {esc(r["existing_summary_utc"])} · matrix revision {r["matrix_revision"]}. {esc(r["snapshot_note"])}</p>','<div class="cards">']
 accepted_n=sum(n for s,n in r['state_counts'].items()if s in[PASS,REF])
 for label,value in[('Frozen inputs',f'{r["frozen_inputs"]}/42; 7 unresolved'),('Accepted cells',f'{accepted_n}/{r["planned_cells"]}'),('Actual starts',b.get('spent','unknown')),('Running confirmed',r['state_counts'].get('RUNNING_CONFIRMED',0)),('Controller dispatch slots',len(b.get('running',[]))),('Postprocessing slots',len(b.get('postprocess',[])))]:out.append(f'<div class="card">{esc(label)}<br><strong>{esc(value)}</strong></div>')
 out+=['</div><p><b>Ratios &gt; 1 mean improvement.</b> DH self = DH P0 / DH variant; CH self = CH P0 / CH variant; relative = DH self / CH self; CH/DH = same-profile CH cycles / DH cycles. Missing, failed and unplanned controls are never zero or imputed. All GMs use one uniform profile. This changing short-job subset is not a final 35-input performance claim.</p>','<p><a href="report.json">Machine-readable report / full SHA evidence</a> · <a href="sensitivity.svg">SVG sensitivity figure</a> · <a href="sensitivity.png">PNG figure</a></p>','<h2>Uniform configuration sensitivity</h2><img src="sensitivity.svg" alt="Sensitivity plot, with matched population sizes"><p>Left: each uniform profile’s available paired population. Right: identical intersection across every registered non-P0 profile, including incomplete profiles; blank means no complete intersection. Different left-panel populations must not be ranked as final suite winners.</p>','<table><tr><th>Profile</th><th>Metric</th><th>GM</th><th>Median</th><th>n / 35</th><th>Positive / neutral / negative</th><th>Missing</th><th>Common four-cell GM / n</th></tr>']
 for f in r['profiles']:
  for k in METRICS:
   s=r['statistics'][f]['ALL'][k];q=r['statistics'][f]['ALL']['common_matched_quad'][k]
   out.append(f'<tr><td>{esc(f)}</td><td>{esc(k)}</td><td>{rfmt(s["GM"])}</td><td>{rfmt(s["median"])}</td><td>{s["n"]}/{s["expected_n"]}</td><td>{s["positive"]} / {s["neutral"]} / {s["negative"]}</td><td>{s["missing_n"]}</td><td>{rfmt(q["GM"])} / {q["n"]}</td></tr>')
 out+=['</table><h2>35 inputs × all profiles</h2><label>Search <input id="search" placeholder="program, suite, full trace SHA"></label><label>Profile <select id="profile"><option value="">All</option>'+''.join(f'<option>{esc(f)}</option>'for f in r['profiles'])+'</select></label><label>Suite <select id="suite"><option value="">All</option>'+''.join(f'<option>{esc(s)}</option>'for s in sorted({p['suite']for p in r['programs'].values()}))+'</select></label><div class="wrap"><table id="matrix"><thead><tr><th>Program / suite / full input SHA</th><th>Profile</th><th>CH cycles / state</th><th>DH cycles / state</th><th>CH self</th><th>DH self</th><th>Relative</th><th>CH/DH</th><th>DH L2 read / miss sectors</th><th>DH DRAM read atoms</th></tr></thead><tbody>']
 for d,p in sorted(r['programs'].items(),key=lambda kv:(kv[1]['suite'],kv[1]['program'])):
  for f in r['profiles']:
   cells=r['table'][d].get(f,{});ch=cells.get('CH',{});dh=cells.get('DH',{});v=r['comparisons'][d][f];cc=dh.get('counters')or{}
   attrs=f'data-search="{esc(p["program"]+" "+p["suite"]+" "+d)}" data-profile="{esc(f)}" data-suite="{esc(p["suite"])}"'
   out.append(f'<tr {attrs}><td>{esc(p["program"])}<small>{esc(p["suite"])}</small><small><code>{d}</code></small></td><td>{esc(f)}</td>')
   for cell in[ch,dh]:
    state=cell.get('state','NOT_PLANNED');out.append(f'<td title="{esc(cell.get("cohort","No registered control"))}">{nfmt(cell.get("cycles"))}<small>{esc(state)}</small></td>')
   for k in['CH_speedup','DH_speedup','relative_DTC_improvement','CH_over_DH']:
    val=v[k];cls='muted'if val is None else'good'if val>1 else'bad'if val<1 else'';out.append(f'<td class="{cls}">{rfmt(val)}</td>')
   out.append(f'<td>{nfmt(cc.get("L2_read_sectors"))} / {nfmt(cc.get("L2_read_miss_sectors"))}</td><td>{nfmt(cc.get("DRAM_read_atoms"))}</td></tr>')
 out+=['</tbody></table></div><h2>Structure resources</h2><p>Counts are configured capacities, not occupancy, bit cost, equal-area evidence or free hardware. Fixed L2 capacity and DRAM clock must remain unchanged. FR-FCFS queue expansion also changes memory-partition credits.</p><table><tr><th>Profile</th><th>MSHR / subpartition</th><th>Merge / entry</th><th>Miss queue / subpartition</th><th>FRFCFS / controller</th><th>Total MSHRs</th><th>Merge slot upper bound</th><th>Total miss slots</th><th>Total FRFCFS slots</th><th>L2 bytes / MHz</th></tr>']
 for f in r['profiles']:
  p=r['profile_parameters'].get(f,{})
  keys=['MSHR_entries_per_subpartition','max_merge_per_MSHR_entry','miss_queue_per_subpartition','FRFCFS_queue_per_controller','total_L2_MSHR_entries','total_MSHR_merge_slots_upper_bound','total_L2_miss_queue_slots','total_FRFCFS_queue_slots']
  out.append('<tr><td>'+esc(f)+'</td>'+''.join('<td>'+nfmt(p.get(k))+'</td>'for k in keys)+f'<td>{nfmt(p.get("L2_total_capacity_bytes"))} / {nfmt(p.get("dram_MHz"))}</td></tr>')
 single=sum(v.get('L2_last_printed_scope')=='SINGLE_STREAM_DECLARED_TRACE_TOTAL'for v in r.get('stream_scopes',{}).values())
 out+=['</table>',f'<p>L2 counter scope: complete single-stream header evidence for {single}/{r["frozen_inputs"]} inputs. Last-printed per-stream cumulative buckets represent the declared-trace total only for those verified inputs. Other whole-trace L2 values are withheld; raw last-stream values remain in JSON. DRAM counters are global cumulative.</p>','<details><summary>Suite statistics and coverage</summary>']
 for f in r['profiles']:
  for group,s in r['statistics'][f].items():
   if group=='ALL':continue
   out.append(f'<p><b>{esc(f)} · {esc(group)}</b> '+'; '.join(f'{esc(k)}: {rfmt(s[k]["GM"])} (n={s[k]["n"]}/{s[k]["expected_n"]}, +/=/− {s[k]["positive"]}/{s[k]["neutral"]}/{s[k]["negative"]})'for k in METRICS)+'</p>')
 out+=['</details><h2>Evidence and limitations</h2><p>L2 MSHR entry-full and merge-full reasons can be absent; aggregate reservation failures do not separate them. Missing latency is not zero. Last-printed average latency is not a weighted whole-application mean. DRAM refresh sentinel is unusable. Trace-population acceptance does not prove full-application numerical values. The seven unresolved inputs remain outside the frozen 35. English v0.23 is unchanged.</p>',f'<p>Generator SHA <code>{r["generator"]["sha256"]}</code>; publication/tool commit <code>{esc(r["generator"]["tool_commit"])}</code>. Exact Core/Framework/binary identities are recorded per accepted cell in report.json. Source root: <code>{esc(r["root"])}</code>.</p>',f'<p>Uniform target-option disagreements: {len(r["uniform_option_errors"])}. Same-population summary GM disagreements: {sum(c["GM_match_on_same_population"]is False for c in r["summary_crosschecks"])}. Unequal populations reflect different acquisition times and are explicitly recorded.</p>','<details><summary>All consumed source files and SHA256</summary><table class="sources"><tr><th>Source</th><th>SHA256</th><th>Bytes</th></tr>']
 for s in r['source_snapshots']:out.append(f'<tr><td><code>{esc(s["path"])}</code></td><td><code>{s["sha256"]}</code></td><td>{s["bytes"]}</td></tr>')
 out+=['</table></details><script>function filter(){let q=document.getElementById("search").value.toLowerCase(),p=document.getElementById("profile").value,s=document.getElementById("suite").value;document.querySelectorAll("#matrix tbody tr").forEach(r=>r.hidden=!(r.dataset.search.toLowerCase().includes(q)&&(!p||r.dataset.profile===p)&&(!s||r.dataset.suite===s)));}["search","profile","suite"].forEach(id=>document.getElementById(id).addEventListener("input",filter));</script></html>']
 return '\n'.join(out)

def plot(r,out):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 variants=[p for p in r['profiles']if p!='P0'];fig,axes=plt.subplots(1,2,figsize=(12.8,4.5),constrained_layout=True)
 for ax in axes:ax.axhline(1,color='#8793a3',lw=1);ax.set_ylabel('Geometric mean speedup');ax.grid(axis='y',alpha=.2)
 colors={'DH_speedup':'#186fbb','CH_speedup':'#b76a1d','relative_DTC_improvement':'#16866b'}
 for k,offset in[('DH_speedup',-.2),('CH_speedup',0),('relative_DTC_improvement',.2)]:
  for i,p in enumerate(variants):
   s=r['statistics'][p]['ALL'][k]
   if s['GM']is not None:
    axes[0].scatter(i+offset,s['GM'],color=colors[k],s=30,label=k if not any(t.get_label()==k for t in axes[0].collections)else None);axes[0].annotate('n='+str(s['n']),(i+offset,s['GM']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7)
   c=r['fixed_all_profile_common_population']['ALL'][k]['by_profile'][p]
   if c['GM']is not None:axes[1].scatter(i+offset,c['GM'],color=colors[k],s=30,label=k if not any(t.get_label()==k for t in axes[1].collections)else None)
 for ax,title in zip(axes,['Available paired inputs (changing partial coverage)','Same inputs across ALL registered variants']):
  ax.set_title(title,fontsize=10);ax.set_xticks(range(len(variants)),variants,rotation=35);ax.set_xlim(-.6,max(.6,len(variants)-.4))
  if not ax.collections:ax.text(.5,.57,'PENDING: no valid matched pairs\nNo missing values imputed',ha='center',transform=ax.transAxes,color='#657385')
  else:ax.legend(fontsize=7,loc='best')
  ys=[float(y)for collection in ax.collections for x,y in collection.get_offsets()]
  ax.set_ylim(min(.95,min(ys)*.98)if ys else .95,max(1.05,max(ys)*1.02)if ys else 1.05)
 axes[1].text(.02,.02,'Common DH n='+str(r['fixed_all_profile_common_population']['ALL']['DH_speedup']['n'])+'; common relative n='+str(r['fixed_all_profile_common_population']['ALL']['relative_DTC_improvement']['n']),transform=axes[1].transAxes,fontsize=7)
 fig.suptitle('DTC L2 concurrency — uniform profiles; '+('PARTIAL'if r['partial']else'complete planned matrix'),fontsize=12)
 fig.savefig(out/'sensitivity.png',dpi=160);fig.savefig(out/'sensitivity.svg');plt.close(fig)

def write_report(r,out):
 out=P(out);out.mkdir(parents=True,exist_ok=True)
 # Only derived artifacts are replaced; source files remain read-only.
 for name,data in[('report.json',encode(r)),('dashboard.html',html_report(r).encode())]:
  tmp=out/(name+'.writing');tmp.write_bytes(data);tmp.replace(out/name)
 plot(r,out)
 manifest=dict(utc=r['utc'],generator=r['generator'],files=[dict(path=n,sha256=sha((out/n).read_bytes()),bytes=(out/n).stat().st_size)for n in['report.json','dashboard.html','sensitivity.png','sensitivity.svg']])
 (out/'REPORT_MANIFEST.json').write_bytes(encode(manifest));return manifest

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='/root/data/dtc_l2_mlp_exploration_20261027_v1');ap.add_argument('--output',required=True);ap.add_argument('--tool-commit',default='UNCOMMITTED_GENERATOR_SHA_IS_CANONICAL');args=ap.parse_args()
 root=P(args.root).resolve();output=P(args.output).resolve()
 assert output!=root and not output.is_relative_to(root),'Output must be independent of live experiment root'
 r=acquire(root,args.tool_commit);m=write_report(r,output)
 print(json.dumps(dict(status='READ_ONLY_REPORT_GENERATED',utc=r['utc'],cells=r['planned_cells'],inputs=r['frozen_inputs'],states=r['state_counts'],uniform_option_errors=len(r['uniform_option_errors']),output=str(output),manifest=m),indent=2))
if __name__=='__main__':main()
