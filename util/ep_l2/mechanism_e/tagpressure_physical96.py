"""Exact remaining2 physical scheduling only. Default original160; no writes.
Root must adopt bounded Writer, BEGIN each new2 journal, then sign/seal policy.
"""
from pathlib import Path
import hashlib,json
import bounded_metadata_writer as bw
MIB=2**20
POLICY_REF={'path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1/engineering/remaining_two_lossless_storage_r1/ACTUAL_BOUNDED_METADATA_POLICY.json', 'sha256': '177e4e272293fde454587a89317e778a30ba8aa5e21b49ca83295c987a3ec41e'} # ROOT seal exact actual signed engineering policy only.
TARGETS=bw.TARGETS
OUTPUT=Path('/workspace/ep_l2_ms20261019_e_results')

def physical_bytes(item,ids,r5):
 r5.require(type(ids)is list and len(ids)==len(set(ids)) and all(cid in r5.CONDITIONS for cid in ids),'exact original physical condition identities')
 if POLICY_REF is None:return len(ids)*160*MIB
 p=r5.read(POLICY_REF);m=r5.scope().manifest()
 r5.require(p.get('schema')=='E2_R5_REMAINING_TWO_BOUNDED_METADATA_ENGINEERING_POLICY_V1' and p.get('status')=='E_ROOT_BOUNDED_WRITERS_ADOPTED_AND_SIGNED','actual root bounded writer policy required')
 r5.require(p.get('condition_ids')==list(TARGETS) and p.get('source_identity')==m['source_identity'] and p.get('final_manifest_ref')==item[r5.FIELD]['manifest_ref'],'same approved new2 source/manifest only')
 r5.require(p.get('activation_actual_starts')==57 and len(item['attempts'])>=57 and p.get('historical57_attempt_prefix_sha256')==r5.sha(item['attempts'][:57]),'actual original paid57 immutable prefix')
 r5.require(not any(a.get('condition_id') in TARGETS for a in item['attempts'][:57]),'no retroactive forecast change')
 r5.require(p.get('physical_per_condition_bytes')==96*MIB and p.get('generation_per_condition_bytes')==160*MIB and p.get('generation_batch_bytes')==640*MIB,'generation unchanged/physical bounded96')
 r5.require(p.get('bounded_writer_rules_actually_adopted') is True and p.get('root_signature') and p.get('independent_review_ref'),'root must actually adopt bounded writers')
 writer_ref=p.get('writer_source_ref',{});r5.require(writer_ref.get('path')==str(Path(bw.__file__).resolve()) and hashlib.sha256(Path(bw.__file__).read_bytes()).hexdigest()==writer_ref.get('sha256'),'actual fixed bounded Writer source required')
 total=0
 for cid in ids:
  if cid not in TARGETS:total+=160*MIB;continue
  activation=r5.read(p['writer_activations'][cid]);root=Path(activation['ledger_root']).resolve()
  r5.require(root.parent==OUTPUT/'E2_R5_BOUNDED_METADATA_PHYSICAL96_ACCOUNTING_r1' and root.name==cid,'exact OUTPUT-owned percondition journal')
  r5.require(activation.get('schema')=='E2_R5_BOUNDED_METADATA_WRITER_ACTIVATED_BEFORE_FORECAST_V1' and activation.get('condition_id')==cid and activation.get('writer_source_ref')==writer_ref and activation.get('root_actual_activation_reviewed') is True,'Writer must be actually begun before mode forecast')
  w=bw.Writer(root,cid,activation['repo'],activation['allowed_roots'],create=False);state=w.state();first=w.journal.read_bytes().splitlines()[0]
  r5.require(hashlib.sha256(first).hexdigest()==activation['journal_begin_sha256'] and state['records'][0].get('physical_cap_bytes')==96*MIB and state['records'][0].get('generation_batch_bytes')==640*MIB,'actual live append-only journal BEGIN proof changed')
  total+=96*MIB
 return total
