#!/usr/bin/env python3
"""Consume only immutable published producer objects; never edits producer lanes."""
from common import *

BINDINGS={
 'AC':dict(framework='2bdadeb5942f90a3216cbf6afbda9dc784d7dfce',core='83aca449135703c176cfab29ae43e1245d00a557',pack='DTC_LANE_AC_COLLECT_PIPELINE_V1'),
 'AD':dict(framework='aa08d184d3e7a141c207ba6ea42f139245561334',core='731be8548ad0fcc167ebfc49d5f1867f22034b4c',pack='DTC_LANE_AD_PROGRESSIVE_WAKE_V1'),
 'AE':dict(framework='3b7c8bca8186add520987f864dd2f67abde87ef3',core='ae83cc510f301cfe7937ad77318e332b2ab324e8',pack='DTC_LANE_AE_TAG_HASH_V1')}

def main():
 receipts=[]
 for lane,b in BINDINGS.items():
  prefix='docs/dtc_l1/review_packs/'+b['pack']+'/'
  paths=git(FW_REPO,'ls-tree','-r','--name-only',b['framework'],prefix).splitlines()
  files=[]
  for p in paths:files.append(copy_blob(FW_REPO,b['framework'],p,'inputs/'+lane+'/'+p[len(prefix):]))
  sums=PACK/'inputs'/lane/'SHA256SUMS'
  for line in sums.read_text().splitlines():
   if not line.strip():continue
   expected,name=line.split(maxsplit=1);name=name.lstrip('*')
   assert sha(sums.parent/name)==expected,(lane,name,'published_manifest_mismatch')
  assert git(CORE_REPO,'merge-base',X2,b['core'])==X2
  changed=git(CORE_REPO,'diff','--name-only',X2,b['core']).splitlines()
  delta=blob(CORE_REPO,b['core'],'src/gpgpu-sim/dtc-l1-common.h')
  receipt=dict(lane=lane,**b,files=files,changed_Core_paths=changed,
      published_pack_manifest='PASS',base_is_fixed_X2=True,
      common_header_sha256=hashlib.sha256(delta).hexdigest())
  if lane=='AD':
   handoff=(PACK/'inputs/AD/AG_HANDOFF.md').read_text()
   assert 'PARTIAL / ON acceptance STOP' in handoff
   receipt.update(qualification='HOLD_UNQUALIFIED',integrate=False,
       reason='Producer explicitly STOPs ON acceptance: new header and real LDST CPU tests not fully passed. No silent model/fixture repair in AG.',
       reserved_slots=[4,5],performance_claim=False)
  elif lane=='AE':
   gate=json.loads((PACK/'inputs/AE/VALIDATION_GATE.json').read_text())
   assert gate['status']=='PASS_BOUNDED_CPU_FRONTEND_READY_FOR_AG'
   source=json.loads((PACK/'inputs/AE/SOURCE_AND_TOOLCHAIN.json').read_text())
   for f in source['source_files']:
    assert hashlib.sha256(blob(CORE_REPO,b['core'],f['path'])).hexdigest()==f['sha256']
   cases=json.loads((PACK/'inputs/AE/CPU_CASES.json').read_text())
   assert len(cases['results'])==137
   receipt.update(qualification='PRODUCER_FRONTEND_PASS_AG_FULL_BUILD_LDST_PENDING',
       integrate='ONLY_AFTER_AG_CPU_GATES',published_cases=137,full_simulations=0)
  else:
   cpu=json.loads((PACK/'inputs/AC/CPU_TEST_RECEIPTS.json').read_text())
   ctest=json.loads((PACK/'inputs/AC/CTEST.json').read_text())
   assert cpu['core']==b['core'] and cpu['status']=='PASS_CPU_REAL_LDST_PIPELINE_SCOPE_ONLY'
   assert len(cpu['processes'])==80 and len(cpu['OFF_state_equivalence'])==17
   assert ctest['status']=='PASS_ORIGINAL_7_PLUS_1_RESOURCE_TEST'
   cost=json.loads((PACK/'inputs/AC/RESOURCE_MODEL.json').read_text())
   assert cost['additional_data_bytes_per_SM']==163840 and cost['banks']==2
   receipt.update(qualification='PRODUCER_REAL_LDST_CPU_PASS_AG_COMBINED_CPU_PENDING',
       integrate='ONLY_AFTER_AG_COMBINED_CPU_GATES',published_processes=80,
       additional_data_bytes_per_SM=163840,full_simulations=0)
  receipts.append(receipt)
 write(PACK/'PUBLISHED_PRODUCER_CONSUMPTION.json',dict(utc=now(),rows=receipts,
     AF_integration=False,new_simulations_started=0))
 print(json.dumps([{k:r[k] for k in ['lane','core','qualification']}for r in receipts]))

if __name__=='__main__':main()
