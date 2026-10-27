import pathlib,json,gzip,hashlib,re,collections,datetime,subprocess
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');d=json.loads((A/'evidence/LEDGER_AUDIT.json').read_bytes());rows=[]
for r in d['current_original']:
 if r['program']not in ['3MM','GEMM','ATAX','MVT','BICG','dwt2d','mri-q']:continue
 for mode,m in r['modes'].items():
  if (m.get('result')or{}).get('state')!='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':continue
  p=P(m['out'])/'raw.log.gz';b=p.read_bytes();raw=gzip.decompress(b);assert hashlib.sha256(b).hexdigest()==m['DONE']['raw_sha256'];assert hashlib.sha256(raw).hexdigest()==m['DONE']['raw_uncompressed_sha256'];lines=raw.decode(errors='replace').splitlines();keylines=collections.defaultdict(list);counter=collections.defaultdict(list)
  for n,line in enumerate(lines,1):
   z=re.match(r'^\s*([\w:.\[\]-]+)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$',line)
   if z:
    k,v=z.groups()
    if k.startswith(('DTC_','gpu_','gpgpu_','L1D_','L2_','averagemf','maxmf','avg_icnt','icnt_')):
     v=float(v)if re.search('[.eE]',v)else int(v);counter[k].append(dict(line=n,value=v))
   if any(k in line for k in ['DTC_L1_','L1D_total','L2_total','GLOBAL_ACC_R[','GLOBAL_ACC_W[','gpu_tot_sim_cycle','gpu_sim_cycle','gpu_occupancy','pipeline duty','gpu_ipc','shader core pipeline','kernel_name']):keylines['lines'].append(dict(line=n,text=line))
  st=m['strict'];metrics=st['metrics'];rows.append(dict(program=r['program'],input_digest=r['input_digest'],mode=mode,cohort=m['cohort'],uuid=m['uuid'],raw_path=str(p),raw_sha256=hashlib.sha256(b).hexdigest(),raw_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),strict_path=m['out']+'/AEFAIR_STRICT.json',strict_cycles=st['cycles'],kernels=st['kernels'],strict_metrics=metrics,strict_traffic=st.get('traffic'),raw_numeric_counters=dict(counter),raw_key_lines=keylines['lines'],strict_actual_core=st.get('core_commit'),strict_actual_framework=st.get('framework_commit'),strict_actual_binary=st.get('binary_sha256'),effective_options=st.get('effective_options')))
out=dict(schema='DTC_P42_EXISTING_ORIGINAL_ACCEPTED_COUNTERS_V1',observed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,new_model_starts=0,raw_files_modified=False,missing_is_null_not_zero=True);(A/'evidence/COUNTERS_RAW_EXTRACT.json').write_text(json.dumps(out,indent=2)+'\n')
for r in rows:
 if r['program']=='3MM'and r['mode']=='DH':print('DTC COUNTER KEYS',list(k for k in r['raw_numeric_counters']if k.startswith('DTC')));print('3MM DH COUNTER SERIES',{k:v for k,v in r['raw_numeric_counters'].items()if k in ['DTC_L1_tag_conflicts','DTC_L1_lower_requests_acquired','L1D_total_cache_misses','L2_total_cache_accesses','gpu_tot_sim_cycle','DTC_L1_pib_occupancy_cycle_sum']})
print('SUMMARY',len(rows),collections.Counter(r['program']for r in rows),collections.Counter((r['strict_actual_core'],r['strict_actual_framework'],r['strict_actual_binary'])for r in rows))
src=P('/root/data/dtc_failure_repair_20261025_v1/core/src');z=subprocess.run(['rg','-n','DTC_L1_|dtc_l1_.*service|pib_occupancy_cycle_sum|logical_tag_set',str(src)],capture_output=True,text=True);(A/'evidence/CORE_COUNTER_SOURCE_SEARCH.txt').write_text(z.stdout);print('CORE matches',len(z.stdout.splitlines()))
