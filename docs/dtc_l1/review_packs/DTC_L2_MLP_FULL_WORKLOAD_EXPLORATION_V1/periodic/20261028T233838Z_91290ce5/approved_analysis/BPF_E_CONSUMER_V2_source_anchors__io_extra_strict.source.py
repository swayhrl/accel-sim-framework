"""Additional IO engineering acceptance AND original strict, no import action."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');ID='SHARED_JSON_IO_OUTER_V1';REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def terminal(c,oldproof):
 assert oldproof['performance_accepted']is True,'Original strict is mandatory'
 intent=read(R/'control/qualification_ledger'/(c+'.INTENT.json'))
 if 'additional_shared_json_io_binding'not in intent:return oldproof
 out=P(intent['output']);documents=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];binding=intent['additional_shared_json_io_binding'];assert all(x['additional_shared_json_io_binding']==binding for x in documents)
 assert binding['schema']==ID and binding['request']==REQ;raw=(out/'SHARED_JSON_IO_SNAPSHOT.json').read_bytes();assert sha(raw)==binding['snapshot_sha256'];snapshot=json.loads(raw);cfg=snapshot['config'];assert binding['config_sha256']==sha(js(dict(cfg,_padding_optin=snapshot['padding_optin'])))
 roles=['source','frontend','extra_strict','owner'];qualified={k:cfg[k+'_sha256']for k in roles};assert binding['qualified_sources']==qualified
 for role in roles:
  source=snapshot['source_snapshots'][role];assert source['sha256']==qualified[role]==sha(source['utf8'].encode())
 assert sha(snapshot['QA_raw_utf8'].encode())==cfg['QA_sha256']and sha(snapshot['readback_raw_utf8'].encode())==cfg['readback_sha256']and json.loads(snapshot['QA_raw_utf8'])==snapshot['QA']and json.loads(snapshot['readback_raw_utf8'])==snapshot['readback']
 qa=snapshot['QA'];back=snapshot['readback'];assert qa['status']=='PASS'and qa['native_prefix_qualified']is True and qa['additional_strict_qualified']is True and back['verified']is True
 assert qa['qualified_sources']==back['qualified_sources']==qualified and qa['expected_pins']==back['expected_pins']==binding['expected_pins']==cfg['expected_pins']
 record=snapshot['operational_overlay_record'];assert record['status']=='ACTIVE'
 for key in['request','overlay_id','expected_pins',*[k+'_sha256'for k in roles+['QA','readback']]]:assert record[key]==cfg[key]
 assert binding['QA_sha256']==cfg['QA_sha256']and binding['readback_sha256']==cfg['readback_sha256']and binding['padding_optin']==snapshot['padding_optin']
 for doc in documents:
  helper=doc['shared_json_publication_binding'];assert helper['source_sha256']==qualified['source']and helper['publication']=='FSYNC_SAME_DIRECTORY_LINK_NOREPLACE'and helper['json_decode_retry_seconds']==1.0 and helper['scientific_completion_rules_unchanged']is True
 if snapshot['padding_optin']:
  proof=oldproof['additional_padding_admission_strict'];assert proof['status']=='PASS_PADDING_ADMISSION_AND_ORIGINAL_STRICT'and sha(P(proof['sidecar_path']).read_bytes())==proof['sidecar_sha256']
 proof=dict(status='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT',original_strict_performance_accepted=True,padding_AND_required=snapshot['padding_optin'],snapshot_sha256=sha(raw),qualified_sources=qualified)
 side=out/'SHARED_JSON_IO_EXTRA_STRICT.json';data=js(proof)
 if side.exists():assert side.read_bytes()==data
 else:
  sp=importlib.util.spec_from_file_location('io_strict_atomic_helper',cfg['source_path']);helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper);assert sha(P(helper.__file__).read_bytes())==qualified['source'];helper.atomic_exclusive(side,proof)
 return dict(oldproof,additional_shared_json_io_strict=dict(proof,sidecar_path=str(side),sidecar_sha256=sha(data)))
