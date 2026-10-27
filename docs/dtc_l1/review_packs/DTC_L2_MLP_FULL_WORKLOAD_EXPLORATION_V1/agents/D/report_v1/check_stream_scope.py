"""Read only qualified header prefixes, never trace bodies or simulation models."""
import pathlib,json,re,hashlib,gzip,datetime,collections
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');scope=json.loads((R/'control/SCOPE.json').read_bytes());seen=set();rows=[]
for p in scope['points']:
 d=p['input_digest']
 if d in seen:continue
 seen.add(d);sp=R/'control/specs'/(p['cohort']+'.json');sb=sp.read_bytes();s=json.loads(sb);bp=pathlib.Path(s['input_binding_path']);bb=bp.read_bytes();binding=json.loads(bb);headers=[]
 for q in binding['qualification']['rows']:
  f=pathlib.Path(q['path'])
  with f.open('rb')as h:magic=h.read(2)
  opener=gzip.open if magic==b'\x1f\x8b'else open
  with opener(f,'rb')as h:
   lines=[]
   for i in range(128):
    b=h.readline(8192)
    if not b or b.startswith(b'#BEGIN_TB'):break
    lines.append(b)
   prefix=b''.join(lines)
  text=prefix.decode();ids=re.findall(r'^-cuda stream id\s*=\s*(\d+)\s*$',text,re.M)
  headers.append(dict(ordinal=q['ordinal'],kernel=q['kernel'],trace_path=str(f),qualified_full_trace_sha256=q['sha256'],header_prefix_sha256=hashlib.sha256(prefix).hexdigest(),header_prefix_bytes=len(prefix),stream_id=int(ids[0])if len(ids)==1 else None,stream_field_count=len(ids)))
 streams=sorted({h['stream_id']for h in headers if h['stream_id']is not None});complete=len(headers)==binding['qualification']['expected_kernels']and all(h['stream_field_count']==1 for h in headers)
 rows.append(dict(program=p['program'],suite=p['suite'],input_digest=d,binding_path=str(bp),binding_sha256=hashlib.sha256(bb).hexdigest(),headers=headers,expected_kernels=binding['qualification']['expected_kernels'],complete_header_coverage=complete,stream_ids=streams,L2_last_printed_scope='SINGLE_STREAM_DECLARED_TRACE_TOTAL'if complete and len(streams)==1 else'MULTISTREAM_REQUIRES_PER_STREAM_LAST_SNAPSHOT_AGGREGATION'if complete else'UNKNOWN_HEADER_COVERAGE'))
print(json.dumps(dict(schema='DTC_L2_MLP_INPUT_STREAM_SCOPE_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=len(rows),kernel_headers=sum(len(r['headers'])for r in rows),scope_counts=dict(collections.Counter(r['L2_last_printed_scope']for r in rows)),rows=rows,rule='Last printed L2 buckets are per-stream cumulative. They represent declared trace total only for a complete single-stream input; whole application numerical correctness is separate. DRAM counters are global cumulative. No missing MSHR reason is assumed zero.'),indent=2))
