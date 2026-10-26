#!/usr/bin/env python3
"""Read-only real frozen data join. This is not pipeline execution or trace qualification."""
import argparse,hashlib,json,pathlib,sys
from audit_common_v1 import Reader,need
from audit_attempt_v1 import admission_for
from check_frozen_identity_inputs_v1 import verify_identity_inputs
from check_production_preservation_v1 import preservation,N,ROOT,ROOT_ACCEPTANCE_SHA
from check_binary_attestation_v1 import check_binary_attestation
SCOPE=N/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json';SCOPE_SHA='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'
def ref(reader,p):
 b=reader.bytes(p);return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--adapter-source',required=True);ap.add_argument('--adapter-sha',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 reader=Reader([N,pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control'),pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')])
 scope=reader.obj(SCOPE);need(ref(reader,SCOPE)['sha256']==SCOPE_SHA,'REAL_SCOPE_PIN_CHANGED')
 accept=reader.obj(ROOT/'ROOT_SCOPE_AND_ACCEPTANCE_V1.json');need(ref(reader,ROOT/'ROOT_SCOPE_AND_ACCEPTANCE_V1.json')['sha256']==ROOT_ACCEPTANCE_SHA,'ROOT_ACCEPTANCE_PIN_CHANGED')
 rows=scope['rows'];need(len(rows)==161 and [x['queue_id'] for x in rows]==accept['frozen_ids'],'REAL_SCOPE_NOT_EXACT161')
 source=pathlib.Path(a.adapter_source);need(ref(reader,source)['sha256']==a.adapter_sha,'ADAPTER_SOURCE_PIN_CHANGED')
 allow={'path':str(source),'sha256':a.adapter_sha}
 index=source.with_name('FROZEN_AUTHORITY_INDEX_V2.json');idx=reader.obj(index)
 for i,row in enumerate(rows):
  item=idx['rows'][i];projection=reader.refobj(item['projection_ref']);job_path=pathlib.Path(projection['identity_row']['job_evidence']['snapshot'])
  result={'inputs':[ref(reader,index),item['projection_ref'],ref(reader,job_path)]}
  verify_identity_inputs(reader,result,row,admission_for(row,i,SCOPE_SHA),allow,True)
 binary=check_binary_attestation(reader,ROOT/'CURRENT_BINARY_ATTESTATION_V1.json',rows)
 saved=preservation(reader,set(x['queue_id'] for x in rows))
 out=pathlib.Path(a.output);audit=N/'auto161_pipeline_20261026_v1/audit'
 need(out.is_absolute() and (out.parent==audit or audit in out.parents) and not out.is_symlink(),'OUTPUT_OUTSIDE_AUDIT')
 report={'schema':'AUTO161_REAL_FROZEN_DATA_JOIN_AUDIT_V1','status':'REAL161_METADATA_JOINS_PASS_NOT_PIPELINE_EXECUTION','exact_ids':161,'adapter_source_path':str(source),'adapter_source_sha256':a.adapter_sha,'binary_attestation':binary,'preservation':saved,'metadata_bytes_independently_reopened':reader.total,'actual_binary_body_bytes_read':0,'production_adapter_invocations':0,'GPU_or_simulator_executions':0,'trace_qualified':0}
 with out.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report))
if __name__=='__main__':main()
