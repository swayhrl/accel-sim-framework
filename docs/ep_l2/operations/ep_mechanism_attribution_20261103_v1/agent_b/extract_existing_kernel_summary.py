import json,pathlib,gzip,hashlib,collections
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1';Q=J/'research/mechanism_attribution_20261103_v1/agent_b'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
metrics=E/'analysis/primary_v1/ACCEPTED_PRIMARY_AND_MATCHED_REFERENCE_METRICS.json';kernels=E/'analysis/primary_v1/T_KERNEL_CYCLE_DECOMPOSITION.json'
base=json.loads(metrics.read_text()); kd=json.loads(kernels.read_text());out=[];total=0
for a,k in zip(base['rows'][:3],kd['rows']):
 p=P(a['point_ref']['path']);assert sha(p)==a['point_ref']['sha256'];point=json.loads(p.read_text());assert point['source_identity']==a['source_identity'];s=P(a['spec_ref']['path']);assert sha(s)==a['spec_ref']['sha256'];spec=json.loads(s.read_text());assert len(spec['expected_effective_options'])==283
 raw=P(k['raw_ref']['path']);assert sha(raw)==k['raw_ref']['sha256']==point['raw_stream_receipt']['stored_sha256']
 size=0;h=hashlib.sha256();keep=[];seen=collections.Counter()
 with gzip.open(raw,'rb')as f:
  for line in f:
   size+=len(line);total+=len(line);assert total<=64*1024*1024;h.update(line)
   if line.startswith((b'EPL2B0V1|',b'EPL2M0AV1|')):
    st=line.decode().strip();parts=st.split('|');fields={x.split('=',1)[0]:x.split('=',1)[1]for x in parts[1:]if'='in x}
    if fields.get('scope')=='kernel':keep.append(dict(family=parts[0],fields=fields));seen[parts[0]]+=1
 assert size==point['raw_stream_receipt']['raw_bytes']and h.hexdigest()==point['raw_stream_receipt']['raw_sha256']
 out.append(dict(mode=a['mode'],point_ref=ref(p),spec_ref=ref(s),raw_ref=ref(raw),source_identity=point['source_identity'],input_identity_sha256=point['input_identity_sha256'],read_uncompressed_bytes=size,raw_uncompressed_sha256=h.hexdigest(),retained_family_counts=dict(seen),records=keep))
result=dict(schema='EP_MAIN_BOUNDED_EXISTING_KERNEL_B0_M0_SUMMARY_V1',model_starts=0,trace_reads=0,uncompressed_read_cap=64*1024*1024,actual_uncompressed_read_bytes=total,filter='only EPL2B0V1/EPL2M0AV1 with explicit scope=kernel; one pass per accepted OFF raw',source_refs=[ref(metrics),ref(kernels)],rows=out)
(Q/'T_ACCEPTED_OFF_KERNEL_RESOURCE_RECORDS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(dict(actual_uncompressed_read_bytes=total,by_arm=[dict(mode=r['mode'],records=r['retained_family_counts'])for r in out],first_record=out[0]['records'][:1]),indent=2))
