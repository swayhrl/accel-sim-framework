#!/usr/bin/env python3
"""Small V3 metadata/state resource edges; no real trace or Native physical paths."""
import pathlib,sys,os,json,hashlib,resource
D=pathlib.Path(__file__).parent;sys.path.insert(0,str(D));os.sched_setaffinity(0,{0,1});os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30))
import sm70_decoder_stream_v3 as A
rows=[]
b=b'MemcpyHtoD,0x1000,8\nkernel-1.traceg\n'
def meta(**kw):return dict(profile='DTC',configuration_profile='DTC_DH',kind='cmdlist',compression='text',size=len(b),sha256=hashlib.sha256(b).hexdigest(),**kw)
with A.Session('DTC','DTC_DH')as s:
 o=s.begin(meta(max_command_bytes=len(b)));o.feed(b);r=o.end();assert o.state is None and o.decoder is None and r['records']==0;rows.append(dict(case='exact_command_byte_cap_and_success_releases_state',PASS=True))
for args in [dict(max_command_bytes=len(b)-1),dict(max_command_bytes=16*2**20+1),dict(max_state_keys=8_000_001),dict(max_state_bytes=40*2**20+1),dict(max_state_keys=True),dict(max_xz_decoder_bytes=True),dict(stream_completion_profile='unknown')]:
 with A.Session('DTC','DTC_DH')as s:
  try:o=s.begin(meta(**args));o.feed(b);o.end()
  except (ValueError,TypeError):rows.append(dict(case=str(args),PASS=True,rejected=True))
  else:raise AssertionError('resource policy accepted')
out=dict(schema='SM70_V3_SMALL_METADATA_RESOURCE_EDGE_FIXTURES_V1',PASS=True,case_count=len(rows),tests=rows,physical_Native_or_GPU=False)
(D/'SMALL_RESOURCE_EDGE_RESULT_V3.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
