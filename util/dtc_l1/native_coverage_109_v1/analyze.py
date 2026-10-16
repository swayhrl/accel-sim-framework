#!/usr/bin/env python3
"""Recompute summaries from independent timing samples and profiler receipts."""
import collections,csv,hashlib,json,pathlib,re,sqlite3,statistics
repo=pathlib.Path(__file__).resolve().parents[3];pack=repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1';raw=pathlib.Path('/data/c16/dtc_native_coverage_109_v1/raw')
assert (raw/'NATIVE_CAMPAIGN_COMPLETE').exists()
reg=json.loads((pack/'PREREGISTRATION.json').read_text());names=reg['diagnostic_conditions']+['SpMV','LayerNorm_1024','LayerNorm_8192']
def dump(n,x):(pack/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def tsv(n,rows):
 with (pack/n).open('w') as f:
  w=csv.DictWriter(f,list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def obj(path):
 lines=path.read_text().splitlines();line=next(l for l in lines if l.startswith('{') or l.startswith('DTC_JSON '));return json.loads(line.removeprefix('DTC_JSON '))
summaries=[];samples=[];profiles=[];candidate_kernels=[]
metrics=json.loads((raw/'EXACT_METRICS.json').read_text())
launch=['launch__registers_per_thread','launch__shared_mem_per_block_static','launch__shared_mem_per_block_dynamic','launch__waves_per_multiprocessor','launch__func_cache_config','launch__occupancy_limit_registers','launch__occupancy_limit_shared_mem']
for name in names:
 batches=[];hashes=set()
 for b in range(7):
  row=obj(raw/f'timing_b{b}_{name}.log');ss=row['samples_ms'];assert len(ss)==10 and all(x>0 for x in ss);batches.append(statistics.median(ss));samples.append(dict(case=name,batch=b,**row))
  if 'input_sha256' in row:hashes.add(row['input_sha256'])
 assert len(hashes)<=1
 med=statistics.median(batches);q=statistics.quantiles(batches,n=4,method='inclusive')
 summaries.append(dict(case=name,batches=7,samples=70,median_of_batch_medians_us=med*1000,batch_median_iqr_us=(q[2]-q[0])*1000,batch_median_mad_us=statistics.median(abs(v-med) for v in batches)*1000,min_batch_median_us=min(batches)*1000,max_batch_median_us=max(batches)*1000))
 rows=[r for r in csv.DictReader((raw/f'ncu_{name}.csv').open()) if r['ID']]
 for order,r in enumerate(rows):
  profiles.append(dict(case=name,kernel_order=order,kernel=r['Kernel Name'],block=r['Block Size'],grid=r['Grid Size'],**{m:r.get(m,'NOT_COLLECTED') for m in metrics+launch}))
 if name in ['SpMV','LayerNorm_1024','LayerNorm_8192']:
  c=sqlite3.connect(raw/f'nsys_{name}.sqlite');c.row_factory=sqlite3.Row
  kernels=list(c.execute('SELECT k.*,s.value as kernel_name FROM CUPTI_ACTIVITY_KIND_KERNEL k JOIN StringIds s ON k.demangledName=s.id ORDER BY k.start'))
  assert len(kernels)==len(rows)==1,'complete operator count mismatch: requires review'
  for k in kernels:
   candidate_kernels.append(dict(case=name,kernel_order=0,kernel=k['kernel_name'],grid=[k[f'grid{x}'] for x in 'XYZ'],block=[k[f'block{x}'] for x in 'XYZ'],registers=k['registersPerThread'],static_shared=k['staticSharedMemory'],dynamic_shared=k['dynamicSharedMemory'],local_bytes_per_thread=k['localMemoryPerThread'],cache_config=k['cacheConfig'],shared_limit_config=k['sharedMemoryLimitConfig'],nsys_kernel_ns=k['end']-k['start'],scope='COMPLETE_OPERATOR_AFTER_3_WARMUPS'))
  c.close()
tsv('TIMING_SUMMARY.tsv',summaries);dump('TIMING_SAMPLES.json',samples);tsv('PROFILE_METRICS.tsv',profiles);dump('ORDERED_OPERATOR_KERNELS.json',candidate_kernels)
for n in ['diagnostic.sass','spmv.sass','LayerNorm_1024_ncu_sass.txt']:
 text=(raw/n).read_text();forms=collections.Counter(re.findall(r'\b(?:LDG|LDGSTS|STG|LDS|STS|LDC|ULDC)(?:\.[A-Z0-9]+)*\b',text));dump(n.replace('.','_')+'_FORMS.json',dict(evidence='STATIC_BINARY_SASS_NOT_DYNAMIC_COUNTS',file=n,sha256=hashlib.sha256((raw/n).read_bytes()).hexdigest(),memory_forms=forms,async_ldgsts_present='LDGSTS' in text))
dump('GPU_LOCK_RECEIPT.json',dict(lock='/data/c16/locks/c16_gpu_campaign.lock',start=(raw/'GPU_LOCK_START_UTC.txt').read_text().strip(),end=(raw/'GPU_LOCK_END_UTC.txt').read_text().strip(),acquisition='FLOCK_EX_NB; no compute processes at start',release='FINALLY; native campaign completed',source_commit=(raw/'PRODUCER_SOURCE_COMMIT.txt').read_text().strip(),clocks_power_modified=False))
for x in summaries:print(x['case'],round(x['median_of_batch_medians_us'],3),'us; batch IQR',round(x['batch_median_iqr_us'],3))
