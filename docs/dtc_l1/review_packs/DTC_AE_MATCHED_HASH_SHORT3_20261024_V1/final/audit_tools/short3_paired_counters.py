"""Typed within-design counter comparisons from already accepted complete runs."""
import pathlib,json
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1')
def read(p):return json.loads(pathlib.Path(p).read_bytes())
KEYS=['L1D_total_cache_accesses','L1D_total_cache_misses','L1D_total_cache_pending_hits','L1D_total_cache_reservation_fails','DTC_L1_oo_valid_hits','DTC_L1_oo_pending_hits','DTC_L1_oo_new_misses','DTC_L1_oo_tag_evictions','DTC_L1_lower_credit_acquired','DTC_L1_lower_requests_acquired','DTC_L1_pib_admits']
def main():
 r=read(T/'analysis/COMPLETE_RESULT.json');rows=[]
 for w in ['NN','DWT2D','MRI-Q']:
  points={p['cell']:p for p in r['points'] if p['workload']==w};data={}
  for c,p in points.items():
   out=pathlib.Path(read(T/'control/qualification_ledger'/(p['cohort']+'.INTENT.json'))['output']);x=read(out/'AEFAIR_STRICT.json');assert x['performance_accepted']
   data[c]={'cycles':x['cycles'],'kernels':x['kernels'],'metrics':{k:x['metrics'].get(k,'UNAVAILABLE_NOT_PRINTED') for k in KEYS},'L2_accepted_read_32B_sectors':x['traffic']['L2_accepted_read_32B_sectors'],'DRAM_issued_read_atoms':x['traffic']['DRAM_issued_read_atoms'],'DRAM_issued_write_atoms':x['traffic']['DRAM_issued_write_atoms']}
  pairs=[]
  for off,on in [('CM','CH'),('DM','DH')]:
   diffs={k:data[on]['metrics'][k]-data[off]['metrics'][k] for k in KEYS if type(data[on]['metrics'][k]) is int and type(data[off]['metrics'][k]) is int}
   kernel_deltas=[{'ordinal':a['ordinal'],'kernel':a['kernel'],'cycles_OFF':a['cycles'],'cycles_ON':b['cycles'],'ON_minus_OFF':b['cycles']-a['cycles']} for a,b in zip(data[off]['kernels'],data[on]['kernels'])]
   pairs.append({'OFF':off,'ON':on,'cycles_ON_minus_OFF':data[on]['cycles']-data[off]['cycles'],'per_kernel_cycle_deltas':kernel_deltas,'numeric_metric_ON_minus_OFF':diffs,'scope':'Within same design only; L1D ordinary-array and DTC logical exports are different populations across designs. Terminal metrics retain their original parser scope; no new direct cause assigned.'})
  rows.append({'workload':w,'points':data,'pairs':pairs})
 out={'schema':'DTC_SHORT3_TYPED_WITHIN_DESIGN_COUNTERS_V1','status':'READ_ONLY_ACCEPTED_OUTPUT_DIAGNOSTICS','workloads':rows,'new_model_starts':0,'missing_fields':'UNAVAILABLE_NOT_PRINTED,neverzero','scope':'Existing bounded model exports only; no unprinted counters or capture-native values inferred'}
 with (T/'analysis/PAIRED_COUNTERS.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
