from pathlib import Path
import json,gzip,hashlib
B=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/B_closed_samples_analysis_v1');O=B.parent/'C_interim_mechanism_review_v1';d=json.loads(gzip.decompress((B/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz').read_bytes()));rows=[]
for r in d['rows']:
 n=0
 for i,k in enumerate(r['kernels']):
  cur=k['positive_only_retry_reasons'];prev={}if i==0 else r['kernels'][i-1]['positive_only_retry_reasons'];want={f:v if i==0 else v-prev[f]if f in prev else None for f,v in cur.items()};assert want==k['positive_only_reason_interval'];n+=sum(v is None for v in want.values())
 rows.append({'program':r['program'],'cell':r['cell'],'profile':r['profile'],'kernel_count':len(r['kernels']),'late_fields_unavailable_not_zero_count':n,'explicit_reason_endpoint_PASS':True})
p=O/'POSITIVE_REASON_ENDPOINT_REVIEW.json';p.write_text(json.dumps({'schema':'C_CLOSED_SAMPLE_POSITIVE_ONLY_REASON_ENDPOINT_REVIEW_V1','all53sources_PASS':True,'rows':rows,'missing_reason_not_imputed_zero':True},indent=2)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest(),sum(x['late_fields_unavailable_not_zero_count']for x in rows))
