"""Read-only replay of shared-JSON binding checks; never calls writing terminal()."""
import hashlib,json,pathlib
P=pathlib.Path
def sha(raw):return hashlib.sha256(raw).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def read(p):return json.loads(P(p).read_bytes())
def audit(root,cohort,result):
 ip=P(root)/'control/qualification_ledger'/(cohort+'.INTENT.json');intent=read(ip)
 if 'additional_shared_json_io_binding'not in intent:
  assert 'additional_shared_json_io_strict'not in result['proof']
  return dict(status='LEGACY_NO_IO_BINDING',intent_path=str(ip),intent_sha256=sha(ip.read_bytes()))
 out=P(intent['output']);documents=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 binding=intent['additional_shared_json_io_binding'];assert all(x['additional_shared_json_io_binding']==binding for x in documents)
 raw=(out/'SHARED_JSON_IO_SNAPSHOT.json').read_bytes();assert sha(raw)==binding['snapshot_sha256'];snapshot=json.loads(raw);cfg=snapshot['config']
 assert binding['config_sha256']==sha(js(dict(cfg,_padding_optin=snapshot['padding_optin'])))
 roles=['source','frontend','extra_strict','owner'];qualified={k:cfg[k+'_sha256']for k in roles};assert binding['qualified_sources']==qualified
 for role in roles:
  source=snapshot['source_snapshots'][role];assert source['sha256']==qualified[role]==sha(source['utf8'].encode())
 assert sha(snapshot['QA_raw_utf8'].encode())==cfg['QA_sha256']and sha(snapshot['readback_raw_utf8'].encode())==cfg['readback_sha256']
 assert json.loads(snapshot['QA_raw_utf8'])==snapshot['QA']and json.loads(snapshot['readback_raw_utf8'])==snapshot['readback']
 qa=snapshot['QA'];back=snapshot['readback'];assert qa['status']=='PASS'and qa['native_prefix_qualified']is True and qa['additional_strict_qualified']is True and back['verified']is True
 assert qa['qualified_sources']==back['qualified_sources']==qualified
 assert qa['expected_pins']==back['expected_pins']==binding['expected_pins']==cfg['expected_pins']
 record=snapshot['operational_overlay_record'];assert record['status']=='ACTIVE'
 for key in ['request','overlay_id','expected_pins',*[k+'_sha256'for k in roles+['QA','readback']]]:assert record[key]==cfg[key]
 assert binding['QA_sha256']==cfg['QA_sha256']and binding['readback_sha256']==cfg['readback_sha256']and binding['padding_optin']==snapshot['padding_optin']
 for doc in documents:
  helper=doc['shared_json_publication_binding'];assert helper['source_sha256']==qualified['source']and helper['publication']=='FSYNC_SAME_DIRECTORY_LINK_NOREPLACE'and helper['json_decode_retry_seconds']==1.0 and helper['scientific_completion_rules_unchanged']is True
 proof=result['proof'];extra=proof['additional_shared_json_io_strict'];sp=P(extra['sidecar_path']);side=read(sp)
 assert sha(sp.read_bytes())==extra['sidecar_sha256']and extra==dict(side,sidecar_path=str(sp),sidecar_sha256=sha(sp.read_bytes()))
 assert side['status']=='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT'and side['original_strict_performance_accepted']is True
 assert side['snapshot_sha256']==sha(raw)and side['qualified_sources']==qualified and side['padding_AND_required']==snapshot['padding_optin']
 padding=None
 if snapshot['padding_optin']:
  padding=proof['additional_padding_admission_strict'];assert padding['status']=='PASS_PADDING_ADMISSION_AND_ORIGINAL_STRICT'
  assert sha(P(padding['sidecar_path']).read_bytes())==padding['sidecar_sha256']
 return dict(status='PASS_READONLY_IO_AND_ORIGINAL_STRICT_CHAIN',intent_path=str(ip),intent_sha256=sha(ip.read_bytes()),
  snapshot_path=str(out/'SHARED_JSON_IO_SNAPSHOT.json'),snapshot_sha256=sha(raw),IO_sidecar_path=str(sp),IO_sidecar_sha256=sha(sp.read_bytes()),
  qualified_sources=qualified,padding_AND_required=snapshot['padding_optin'],padding_sidecar=padding,
  source_strict_path=str(P(root)/'control/operational_amendments/shared_json_io_v1/io_extra_strict.py'),
  source_strict_sha256=sha((P(root)/'control/operational_amendments/shared_json_io_v1/io_extra_strict.py').read_bytes()),writes=0)
