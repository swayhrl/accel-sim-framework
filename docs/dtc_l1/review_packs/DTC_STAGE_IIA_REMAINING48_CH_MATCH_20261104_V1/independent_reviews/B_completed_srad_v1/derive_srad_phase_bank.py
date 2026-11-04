from pathlib import Path
import json,gzip,hashlib,re,math,collections
D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(n,v):(D/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
rs=json.load(gzip.open(D/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz','rt'))['rows'];checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
selectors=json.loads((D/'A_PINNED_PHASE_SELECTOR_REFERENCE.json').read_bytes());ck('A144fmanifestpin',sha(Path(selectors['source_manifest']['path']).read_bytes())==selectors['source_manifest']['sha256']);seqp=Path(selectors['trace_sequence']['path']);ck('Atrace_sequence_pin',sha(seqp.read_bytes())==selectors['trace_sequence']['sha256']);seq=json.load(gzip.open(seqp,'rt'))['rows'];overlay={(x['input_digest'],x['kernel_ordinal']):x for x in seq};phaseidx={};by={(r['program'],r['cell'],r['profile']):r for r in rs};phase_rows=[]
for name in ['srad_v1']:
 ref=by[name,'CH','P0'];digest=ref['input_digest'];ps=selectors['programs'].get(digest)
 if ps:
  idx={}
  for ph in ps['phases']:
   x=ph['kernel_ordinals'];ords=list(range(x['first'],x['last_inclusive']+1,x['step']));ck(name+ph['phase_id']+'_selector_count',len(ords)==x['count'])
   for i in ords:ck(name+'_disjoint_'+str(i),i not in idx);idx[i]={'phase_id':ph['phase_id'],'source_stage':ph['source_stage'],'evidence':'A144f_CANDIDATE_SOURCE_TRACE_SEQUENCE_NOT_CAPTURE_ELF'}
  ck(name+'_coverage',set(idx)==set(range(1,ref['kernel_count']+1)))
 else:idx={k['ordinal']:{'phase_id':'TRACE_SYMBOL::'+k['kernel'],'source_stage':'candidate stencil repeated update','evidence':'FIXED_ATLAS_CANDIDATE_SOURCE_AND_EXACT_TRACE_SYMBOL'}for k in ref['kernels']}
 phaseidx[digest]=idx
 for c in ['CH','DH']:
  for p in ['P0','F128','F256']:
   r=by[name,c,p];binding=json.loads(Path(r['input_binding_path']).read_bytes());q=binding['qualification']['rows'];groups={}
   for k,x in zip(r['kernels'],q):
    if ps:
     t=overlay[digest,k['ordinal']];ck(name+c+p+'_traceoverlay_'+str(k['ordinal']),t['symbol']==k['kernel']and t['active_thread_instructions']==k['instructions']and t['trace_sha256']==x['sha256'])
    ph=idx[k['ordinal']];g=groups.setdefault(ph['phase_id'],{'program':name,'input_digest':digest,'cell':c,'profile':p,'phase_candidate':ph,'ordinals':[],'cycles':0,'fields':collections.defaultdict(list)});g['ordinals'].append(k['ordinal']);g['cycles']+=k['cycles']
    for key in r['totals']:g['fields'][key].append(k['print_interval_additive'].get(key))
   for g in groups.values():
    phase_rows.append({k:g[k]for k in ['program','input_digest','cell','profile','phase_candidate','ordinals','cycles']}|{'additive':{key:{'value':sum(v)if all(x is not None for x in v)else None,'missing_intervals':sum(x is None for x in v)}for key,v in g['fields'].items()},'means_gauges_peaks_excluded':True,'myocyte_step_or_3DCONV_scalar_i':None})
   ck(name+c+p+'_phase_cycles_sum',sum(g['cycles']for g in groups.values())==r['cycles'])
put('EXACT_PHASE_MAPPING_AND_COUNTERS.json',phase_rows);pby={(x['program'],x['cell'],x['profile'],x['phase_candidate']['phase_id']):x for x in phase_rows};changes=[]
for name in ['srad_v1']:
 for c in ['CH','DH']:
  for p in ['F128','F256']:
   rows=[]
   for x in phase_rows:
    if x['program']==name and x['cell']==c and x['profile']==p:
     b=pby[name,c,'P0',x['phase_candidate']['phase_id']];rows.append({'phase':x['phase_candidate'],'cycles_P0':b['cycles'],'cycles_variant':x['cycles'],'delta':x['cycles']-b['cycles'],'fields':{key:{'P0':b['additive'][key]['value'],'variant':v['value'],'delta':v['value']-b['additive'][key]['value']if v['value']is not None and b['additive'][key]['value']is not None else None}for key,v in x['additive'].items()}})
   ck(name+c+p+'_phase_delta_reconciles',sum(x['delta']for x in rows)==by[name,c,p]['cycles']-by[name,c,'P0']['cycles']);changes.append({'program':name,'cell':c,'profile':p,'phases':rows})
put('PHASE_COMPARISONS.json',changes)
# Existing closed raw only; retain just the last printed kernel block. Bank n_access is READ-column atoms only in fixed source.
controllers=[]
for r in rs:
 tail=[];h=hashlib.sha256()
 with gzip.open(r['raw_gzip_path'],'rb')as f:
  for b in f:
   h.update(b)
   if b.startswith(b'kernel_name = '):tail=[]
   tail.append(b.decode(errors='replace'))
 ck(r['program']+r['cell']+r['profile']+'_bank_raw_plain_SHA',h.hexdigest()==r['raw_plain_sha256']);text=''.join(tail);starts=list(re.finditer(r'^DRAM\[(\d+)\]:',text,re.M));ck(r['program']+r['cell']+r['profile']+'_20_controller_blocks',len(starts)==20);cr=[]
 for i,m in enumerate(starts):
  t=text[m.start():starts[i+1].start()if i+1<len(starts)else len(text)];cid=int(m[1]);nline=re.search(r'^n_cmd=[^\r\n]+',t,re.M)[0];nums={k:int(v)for k,v in re.findall(r'\b(n_cmd|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',nline)};banks=[{'bank':int(j),'read_atoms':int(a),'printed_idle_counter':int(z)}for j,a,z in re.findall(r'bk(\d+): (\d+)a (\d+)i',t)];ck(r['program']+r['cell']+r['profile']+'_bank16_ctr'+str(cid),len(banks)==16 and sum(x['read_atoms']for x in banks)==nums['n_rd']+nums['n_rd_L2_A']);q=re.search(r'^queue_avg = (\S+)',t,re.M);mq=re.search(r'^mrqq: max=(\d+) avg=(\S+)',t,re.M);cr.append({'controller':cid,'cumulative':nums,'banks_READ_atoms_only':banks,'FRFCFS_pending_queue_mean_printed':float(q[1])if q else None,'FRFCFS_pending_queue_max_snapshot':int(mq[1])if mq else None,'queue_window_caveat':'Printed pending/scheduler diagnostic; not end-to-end request lifetime. Mean/gauge/peak snapshots never differenced.'})
 ck(r['program']+r['cell']+r['profile']+'_bank_total_matches_all_DRAM_read',sum(sum(x['read_atoms']for x in c['banks_READ_atoms_only'])for c in cr)==r['totals']['DRAM_read_atoms32B']);v=[c['cumulative']['n_rd']+c['cumulative']['n_rd_L2_A']for c in cr];mean=sum(v)/len(v);cv=math.sqrt(sum((x-mean)**2for x in v)/len(v))/mean if mean else None;nonzero=sorted(set(x['bank']for c in cr for x in c['banks_READ_atoms_only']if x['read_atoms']>0));controllers.append({'program':r['program'],'cell':r['cell'],'profile':r['profile'],'source_RESULT_sha256':r['RESULT_sha256'],'raw_plain_sha256':r['raw_plain_sha256'],'scope':'Final cumulative replay READ atoms only; not writes, simultaneous BLP, phase-local queue peaks or short-time bank hotspots.','controllers':cr,'controller_total_read_CV':cv,'banks_with_nonzero_printed_READ_atoms':nonzero,'means_gauges_peaks_not_differenced':True})
(D/'FINAL_CONTROLLER_READ_QUEUE_DIAGNOSTICS.json.gz').write_bytes(gzip.compress((json.dumps({'rows':controllers},separators=(',',':'))+'\n').encode(),mtime=0));src=Path('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dram.cc');b=src.read_bytes();lines=b.decode().splitlines();put('BANK_COUNTER_SOURCE_BOUNDARY.json',{'core_commit':'9eedb3131937748f0492fa83aad37d3691118d70','path':str(src),'sha256':sha(b),'READ_branch_lines555_595':'\n'.join(str(i+1)+': '+lines[i]for i in range(554,595)),'WRITE_branch_lines596_628':'\n'.join(str(i+1)+': '+lines[i]for i in range(595,628)),'print_lines704_709':'\n'.join(str(i+1)+': '+lines[i]for i in range(703,709)),'meaning':'bk.n_access increments only at issued READ including L2 read allocation. Printed a excludes WR/WB; zero a does not mean idle bank or no write/activation. Whole replay cumulative balance does not establish temporal balance.'});put('PHASE_AND_BANK_CPU_VALIDATION.json',{'checks':checks,'all_pass':True,'count':len(checks),'no_live_raw':True,'new_models':0,'final24_not_invoked':True});print('PHASE_BANK_CHECKS',len(checks))
for x in changes:print(x['program'],x['cell'],x['profile'],[(p['phase']['source_stage'],p['delta'])for p in x['phases']])
for x in controllers:print('BANK',x['program'],x['cell'],x['profile'],x['controller_total_read_CV'],x['banks_with_nonzero_printed_READ_atoms'])
