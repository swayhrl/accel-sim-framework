#!/usr/bin/python3
"""Exact Gaussian16 full grouped-record CPU reader. No GPU/application execution."""
from pathlib import Path
import argparse,json,hashlib,subprocess,re
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--traces',required=True);p.add_argument('--reader',required=True);p.add_argument('--out',required=True);p.add_argument('--expected-launches',type=int,default=30);a=p.parse_args()
 root=Path(a.traces).resolve();reader=Path(a.reader).resolve();assert 1<=a.expected_launches<=30
 lists=sorted(root.glob('kernelslist*.g'));assert len(lists)==1,'one exact grouped commandlist required'
 commands=[x.strip()for x in lists[0].read_text().splitlines()if x.strip()];memcpy=[x for x in commands if x.startswith('Memcpy')];assert all(re.fullmatch(r'MemcpyHtoD,\s*(?:0x)?[0-9a-fA-F]+,\s*[0-9]+',x)for x in memcpy),'unknown memcpy command';names=[x for x in commands if not x.startswith('Memcpy')];assert len(names)==a.expected_launches and len(set(names))==len(names)
 rows=[]
 for name in names:
  assert re.fullmatch(r'kernel-[0-9]+(?:-ctx_0x[0-9a-fA-F]+)?\.traceg(?:\.xz)?',name),'unknown grouped command'
  target=root/name;assert target.resolve().is_relative_to(root)
  c=subprocess.run([str(reader),str(target)],capture_output=True,text=True,timeout=120)
  assert c.returncode==0,(name,c.returncode,c.stderr[-1000:])
  matches=[x.split('GAUSSIAN_CPU_FULL_TRACE_JSON ',1)[1]for x in c.stdout.splitlines()if x.startswith('GAUSSIAN_CPU_FULL_TRACE_JSON ')]
  assert len(matches)==1;v=json.loads(matches[0]);assert v['all_CTA_warp_EXIT_CFI_closed']and v['EOF_decompressor_closed'];rows.append(dict(trace_ref=ref(target),result=v))
 assert sorted(x['result']['kernel_id']for x in rows)==list(range(1,a.expected_launches+1))
 report=dict(schema='GAUSSIAN16_FULL_RECORD_CFI_READER_V3',status='PASS',launches=len(rows),
  call_issues=sum(x['result']['CALL_issue_records']for x in rows),ret_issues=sum(x['result']['RET_issue_records']for x in rows),
  call_effective_lanes=sum(x['result']['CALL_effective_lanes']for x in rows),ret_effective_lanes=sum(x['result']['RET_effective_lanes']for x in rows),
  exit_effective_lanes_by_launch={str(x["result"]["kernel_id"]):x["result"]["EXIT_effective_lanes"]for x in rows},source_records=sum(x['result']['source_records']for x in rows),
  static_control_sites=[dict(owner='_Z4Fan1PfS_ii',pc=0x280,kind=1),dict(owner='_Z4Fan1PfS_ii',pc=0x960,kind=2)],
  commandlist_memcpy_commands=memcpy,full_record_complete=True,loaded_map_complete=True,reader_ref=ref(reader),raw_inputs_refs=[],sidecar_refs=[ref(root/x)for x in ['semantic-map.tsv','ada-loaded.tsv','ada-static.tsv']],rows=rows,
  profile='GAUSSIAN16_DIRECT_RETPAIR_INPUT_OBSERVER_V2_CANDIDATE',device_observer_joined=False,input_numeric_qualification=False,simulator_qualification=False,trace_zero_is_not_independent_zero_evidence=True,fixture_or_partial_launch_override=a.expected_launches!=30)
 Path(a.out).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['rows','sidecar_refs','raw_inputs_refs']}))
if __name__=='__main__':main()
