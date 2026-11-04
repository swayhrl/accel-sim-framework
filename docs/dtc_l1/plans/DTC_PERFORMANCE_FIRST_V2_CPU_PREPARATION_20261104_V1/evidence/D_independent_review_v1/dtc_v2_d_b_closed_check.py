import pathlib,json,hashlib,gzip,re,math,collections
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');D=V/'agents/D_independent_review_v1';B=V/'agents/B_mechanisms_v1/snapshots/capture11_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
mf=B/'MANIFEST.json';ck('Frozen B mechanism snapshot manifest',sha(mf)=='47bff0cdf7290fa3b9822c7ccb6b187b66e506d8140903edb081da0a3182b437')
for z in json.loads(mf.read_text())['files']:
 p=B/z.get('path',z.get('relative_path',z.get('name')));ck('Mechanism snapshot member '+p.name,sha(p)==z['sha256'])
j=json.loads(gzip.decompress((B/'KERNEL_COUNTER_EVIDENCE.json.gz').read_bytes()));comp=json.loads((B/'MATCHED_COMPARISONS.json').read_text());details=[]
for s in j['sources']:
 if s['program'] not in ('MVT','BICG') or s['cell']!='DH':continue
 pins=['RESULT','bottom_RESULT','native_EXIT','raw_gzip']
 for k in pins:ck(s['program']+' '+s['profile']+' '+k+' SHA',sha(pathlib.Path(s[k]['path']))==s[k]['sha256'])
 r=json.loads(pathlib.Path(s['RESULT']['path']).read_text());ev=json.loads(pathlib.Path(s['native_EXIT']['path']).read_text());ck('Source is performance accepted before raw read '+s['program']+s['profile'],r['proof']['performance_accepted'] is True and ev['launcher_wait_returncode']==0 and ev['stop_reason'] is None)
 raw=gzip.decompress(pathlib.Path(s['raw_gzip']['path']).read_bytes());ck('Closed raw decompressed SHA '+s['program']+s['profile'],hashlib.sha256(raw).hexdigest()==s['raw_uncompressed_sha256'])
 text=raw.decode();starts=list(re.finditer(r'^kernel_name = (\S+)',text,re.M));kern=[]
 for ii,begin in enumerate(starts):
  block=text[begin.start():starts[ii+1].start() if ii+1<len(starts) else None]
  n={a:int(b) for a,b in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',block,re.M)}
  ctrl=[]
  for ln in block.splitlines():
   if ln.startswith('n_cmd='):
    row={a:int(b) for a,b in re.findall(r'\b(n_rd|n_rd_L2_A|n_write|n_wr_bk|n_req)=(\d+)',ln)}
    if len(row)==5:ctrl.append(row)
  ck('20 DRAM controller rows '+s['program']+s['profile']+str(ii),len(ctrl)==20)
  got={'cycles':n['gpu_sim_cycle'],'oo_new_misses':n['DTC_L1_oo_new_misses'],'lower_created':n['DTC_L1_oo_lower_created'],'DRAM_read_atoms32B':sum(z['n_rd']+z['n_rd_L2_A'] for z in ctrl),'postready_sum':n['DTC_SERVICE_V1_fully_ready_to_complete_sum'],'wb_wait':n['DTC_SERVICE_V1_wb_wait']}
  ks=s['kernels'][ii];ck('Kernel name and cycles '+s['program']+str(ii),begin.group(1)==ks['kernel'] and got['cycles']==ks['cycles'])
  for a,b in [('oo_new_misses','DTC_L1_oo_new_misses'),('lower_created','DTC_L1_oo_lower_created'),('DRAM_read_atoms32B','DRAM_read_atoms32B'),('postready_sum','DTC_SERVICE_V1_fully_ready_to_complete_sum'),('wb_wait','DTC_SERVICE_V1_wb_wait')]:ck('Independent raw counter '+s['program']+s['profile']+str(ii)+a,got[a]==ks['cumulative_additive'][b])
  kern.append(got)
 ck('Kernel cycle sum '+s['program']+s['profile'],sum(z['cycles'] for z in kern)==s['cycles'])
 details.append({'program':s['program'],'profile':s['profile'],'cycles':s['cycles'],'kernels':kern,'RESULT_sha256':s['RESULT']['sha256'],'closed_raw_sha256':s['raw_gzip']['sha256']})
for row in comp:
 c=row['cycles'];ck('Derived candidate speedup '+row['program']+row['variant'],math.isclose(row['S_DH'],c['DH_P0']/c['DH_candidate'],rel_tol=1e-14))
 ck('Derived absolute CH/candidate '+row['program']+row['variant'],math.isclose(row['Rnew'],c['CH_P0']/c['DH_candidate'],rel_tol=1e-14))
 for name,x in row['within_DH_additive_changes'].items():
  expected=None if x['P0'] is None or x['candidate'] is None else x['candidate']-x['P0'];ck('Typed counter delta '+row['program']+row['variant']+name,x['delta']==expected)
focus={}
for program in ['MVT','BICG']:
 r=next(z for z in comp if z['program']==program and z['variant']=='PHYS768_TAG64x8');focus[program]={'cycles':r['cycles'],'S_DH':r['S_DH'],'CH0_over_candidate':r['Rnew'],'changes':{}}
 for key in ['DTC_L1_oo_new_misses','DTC_L1_oo_lower_created','DRAM_read_atoms32B','DTC_SERVICE_V1_fully_ready_to_complete_sum','DTC_SERVICE_V1_wb_wait']:
  x=r['within_DH_additive_changes'][key];focus[program]['changes'][key]={'P0':x['P0'],'candidate':x['candidate'],'fractional_change':None if not x['P0'] else x['candidate']/x['P0']-1}
out={'scope':'Independent read of exactly four already closed DH-P0/PHYS768 raw streams (MVT/BICG), with prior accepted proof/EXIT and full raw SHA gate; no active raw. Additional B11 arithmetic/typed-null review, not new lifecycle or whole archive re-audit.','checks':checks,'closed_sources':details,'focus':focus,'B_manifest':str(mf),'B_manifest_sha256':sha(mf),'V2_new_models':0,'V1_writes':0}
p=D/'INDEPENDENT_MVT_BICG_CLOSED_EVIDENCE_REVIEW.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'all_PASS':True,'sha256':sha(p),'focus':focus}))
