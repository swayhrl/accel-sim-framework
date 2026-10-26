#!/usr/bin/env python3
"""Postrun E2 terminal/archive route equivalence; never launch or requalify a model."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib
import experiment_runtime as v
import e2_fresh_input_dispatch as e2
P=pathlib.Path
PEER_SHA='383a308c2e42e2cd59b1a5e0d537649db51dbb99d8fd31df594dd5280b51aba7'
OLD_SHA='dc7c232b944691379aaa42417abd7d622114abc148ecb6fdf72aebf6ecbf3f66'
PEER_PREFIX='''#!/bin/sh
set -eu
# Exact DTC continuation prefixes; EP and other routes below are preserved.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-AEV100-*|experiment:E2-AEREPAIR-LAVAMEM2-*|experiment:E2-AEREPAIR-LATE4-*|experiment:E2-AEREPAIR-REMAIN4-*|result:E2-AEREPAIR-REMAIN4-*)
   exec /usr/bin/python3 -B /root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1/tools/remaining_frontend_v1.py "$@"
   ;;
 esac
fi
'''
WRAPPER='''#!/bin/sh
set -eu
if [ "$#" -ge 3 ]; then
 case "$1:$2:$3" in
  experiment:accept:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1|result:archive:EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1)
   exec /usr/bin/python3 -B /root/data/ep_memory_path_sensitivity_20261026_v1/tools/e2_postrun_entry_adapter.py "$@"
   ;;
 esac
fi
exec /bin/sh /root/data/ep_memory_path_sensitivity_20261026_v1/tools/peer_extended_native_entry.sh "$@"
'''
def postrun_pins():
 s=v.spec();b=v.read(v.B/'control/SPEC_AUTHORIZATION_BINDING.json')
 v.need(v.sha(v.B/'control/FROZEN_SPEC.json')==b['spec_sha256'],'spec drift')
 v.need(v.sha(v.B/'control/USER_AUTHORIZATION.json')==b['authorization_sha256'],'authorization drift')
 v.need(s['cohort']==v.E2 and s['application_budget']==1 and s['automatic_retry'] is False,'finite scope mismatch')
 old=v.ROOT/'tools/native_entry_e2_candidate.sh';peer=v.ROOT/'tools/peer_extended_native_entry.sh'
 v.need(v.sha(old)==OLD_SHA and v.sha(peer)==PEER_SHA,'entry lineage snapshot drift')
 header=b'#!/bin/sh\nset -eu\n'
 v.need(old.read_bytes().startswith(header),'original wrapper header')
 v.need(peer.read_bytes()==PEER_PREFIX.encode()+old.read_bytes()[len(header):],'peer changed original EP route body')
 v.need((v.N/'bin/native').read_bytes()==WRAPPER.encode(),'current postrun entry drift')
 for p,h in s['pinned_files'].items():
  if p==str(v.N/'bin/native'):v.need(h==OLD_SHA,'wrong historical entry pin')
  else:v.need(v.sha(p)==h,'pinned file changed '+p)
 for p,h in s['env_hashes'].items():v.need(v.sha(p)==h,'env changed '+p)
 return s
def main(args):
 v.need(len(args)>=3 and tuple(args[:2]) in [('experiment','accept'),('result','archive')] and args[2]==v.E2,'postrun accept/archive only')
 v.bind(v.E2);s=postrun_pins()
 done=v.read(v.LED/(v.E2+'.DONE.json'))
 v.need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural terminal required')
 out=P(done['output'])
 v.need(v.sha(out/'raw.log')==done['raw_sha256'],'immutable closed raw required')
 actual=v.read(out/'NATIVE_LAUNCH.json')
 v.need(actual['spec_sha256']==v.sha(v.B/'control/FROZEN_SPEC.json') and actual['source_identity']==s['source_identity'],'actual launch binding')
 proof={'schema':'EP_E2_POSTRUN_ENTRY_ROUTE_EQUIVALENCE_V1','status':'PASS_POSTRUN_ONLY',
 'original_spec_entry_sha256':OLD_SHA,'peer_extended_entry_sha256':PEER_SHA,
 'postrun_entry_sha256':v.sha(v.N/'bin/native'),'adapter_sha256':v.sha(__file__),
 'spec_sha256':v.sha(v.B/'control/FROZEN_SPEC.json'),'raw_sha256':done['raw_sha256'],'uuid':done['uuid'],
 'only_pin_exception':str(v.N/'bin/native'),'all_other_pins_and_env_exact':True,
 'peer_prefix_scope':'DTC experiment E2-AEV100/E2-AEREPAIR and result E2-AEREPAIR-REMAIN4; none matches EP_NATIVE_VECTOR',
 'original_EP_route_body_byte_exact':True,'frozen_spec_or_source_modified':False,
 'new_model_forks':0,'new_help_forks':0,'scientific_acceptance_granted_by_proof':False}
 p=out/'POSTRUN_ENTRY_ROUTE_EQUIVALENCE.json'
 if p.exists():v.need(v.read(p)==proof,'postrun proof collision')
 else:v.put(p,proof)
 v.pins=postrun_pins
 return e2.main(args)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as exc:print(json.dumps({'status':'HOLD','reason':str(exc),'automatic_retry':False}),file=sys.stderr);sys.exit(2)
