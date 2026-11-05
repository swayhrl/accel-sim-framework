# Included in the separate broad observation strict source.
ACTUAL_FOUR_GATE_SHA='2a5422d1097c2e6578ff3ba4b2769a64918378bd120c35a305c7ab90c8e990b9'
ACTUAL_FOUR_SOURCE_SHA='4d511441316523a833009d1e354e750d5cb60432fea4a39f8cec9771eeef1c1e'
def load_pinned(path,expected,name):
 require(sha(path)==expected,'Pinned helper/source drift '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify_release_prerequisite(cfg,authority,resource_configuration_utf8=None,resource_snapshot=None):
 """Use actual Main capture plus separate actual Main operational approval.

 This performs no raw archive replay and no authority call, and never grants.
 Historical replay may supply the INTENT-captured resource config.
 """
 resource_text=P(cfg['resource_configuration_path']).read_text()if resource_configuration_utf8 is None else resource_configuration_utf8
 require(utfsha(resource_text)==cfg['resource_configuration_sha256'],'Broad captured resource config SHA')
 rcfg=json.loads(resource_text)
 require(cfg['memory_configuration_path']==cfg['resource_configuration_path'],'Typed memory must refer to new broad resource')
 lib=load_pinned(rcfg['source_paths']['library'],rcfg['qualified_sources']['library'],'broad_release_actual_resource_library')
 require(lib.ID=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1','Wrong broad resource generation')
 if resource_snapshot is None:evidence=lib.validate_broad_approval(rcfg,authority)
 else:
  require(resource_snapshot['config']==rcfg,'Historical resource snapshot generation differs')
  evidence=lib.validate_broad_approval(rcfg,authority,resource_snapshot['broad_approval_utf8'],resource_snapshot['broad_gate_utf8'],resource_snapshot['broad_source_artifacts_utf8'],resource_snapshot['scope_contract_utf8'])
 app=json.loads(evidence['certificate_utf8']);gate=json.loads(evidence['gate_utf8'])
 gr=app['actual_gate']
 require(gr['path']==cfg['canary4_prerequisite_path']and gr['sha256']==cfg['canary4_prerequisite_sha256']==ACTUAL_FOUR_GATE_SHA,'Actual Main mixed-four prerequisite identity')
 require(gr['source_sha256']==gate['gate_source_sha256']==ACTUAL_FOUR_SOURCE_SHA and sha(gr['source_path'])==ACTUAL_FOUR_SOURCE_SHA,'Actual mixed-four replay source bytes')
 require(utfsha(evidence['gate_utf8'])==ACTUAL_FOUR_GATE_SHA and gate['actual_owner_pid']==1498278 and gate['actual_owner_start_ticks']==977758783,'Actual same-owner gate generation')
 for row in gate['rows']:
  require(authority['consumed'][row['cohort']]['uuid']==row['uuid'],'Actual four consumed UUID changed')
  result=json.loads(evidence['source_artifacts_utf8'][row['cohort']+'.RESULT'])
  require(result['proof']['performance_accepted']is True and result['proof']['uuid']==row['uuid'],'Four original performance proof identity')
  require({k:result['proof'][k]for k in ['CTA','instructions','kernel_count']}==row['counts'],'Actual four counts changed')
  require(result['primary_statistics_excluded']is True and result['validated_union_authorized']is False,'Engineering four statistics isolation changed')
 return dict(status='PASS_ACTUAL_MAIN_MIXED_FOUR_AND_EXPLICIT_BROAD_SCOPE',production_release_eligible=not cfg['qualification_only']and not authority.get('qualification_only',False),prerequisite_sha256=ACTUAL_FOUR_GATE_SHA,broad_approval_sha256=rcfg['broad_approval_sha256'],scope_contract_sha256=rcfg['scope_contract_sha256'])
