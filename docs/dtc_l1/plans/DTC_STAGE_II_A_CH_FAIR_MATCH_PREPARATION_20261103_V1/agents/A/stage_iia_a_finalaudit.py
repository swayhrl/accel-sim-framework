from pathlib import Path
import json,hashlib,importlib.util,collections
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/A');R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();M=json.loads((O/'CH_CANDIDATE_MATRIX.json').read_text());I=json.loads((O/'INPUT_SHA_AND_COVERAGE.json').read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
spec=importlib.util.spec_from_file_location('g',R/'tools/l2_config_generator.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
for row in I['inputs']:
 b=json.loads(Path(row['input_binding']['path']).read_text());ck(row['program']+'_binding_digest_equal',b['input_digest']==row['input_digest']);ck(row['program']+'_expected_kernel_count',b['asset']['kernel_launches']==row['expected']['kernels']);ck(row['program']+'_complete_body_status',b['qualification']['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS')
for row in M['candidates']:
 ch=json.loads(Path(row['original_parent_spec']['path']).read_text());dh=json.loads(Path(row['original_DH_variant_spec']['path']).read_text());n=row['candidate_id']
 ck(n+'_input_and_expected',ch['input_digest']==dh['input_digest']==row['input_digest'] and ch['expected']==dh['expected']==row['expected'])
 ck(n+'_fixed_build',ch['core_commit']==dh['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70' and ch['framework_commit']==dh['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and ch['binary_sha256']==dh['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')
 ck(n+'_actual_DH_config_SHAs',all(H(c['path'])==c['sha256']for c in dh['configs']))
 actualch=g.effective_options([(O/c['path']).read_text()for c in row['configs']]);actualdh=g.effective_options([Path(c['path']).read_text()for c in dh['configs']]);diff={k for k in set(actualch)|set(actualdh)if actualch.get(k)!=actualdh.get(k)};ck(n+'_actual_byteparsed_nonL1_equal',diff==set(row['CH_DH_exact_L1_differences']))
 ck(n+'_new_native_spec_absent',not (R/'control/specs'/f"{n}.json").exists() and row['runtime_uuid']is None and row['scientific_execution_authorized']is False)
put={'status':'PASS','models_started':0,'scientific_registrations':0,'loop_assertions':len(checks),'independent_families':8,'families':['Binding digest equality','Declared kernel count equality','Existing complete-body qualification status','CH/DH/input expected coverage equality','Fixed Core/FW/binary equality','Actual DH config file SHA','Actual CH/DH byte-parsed non-L1 equality','No native spec/UUID/execution authority'],'checks':checks}
(O/'CPU_IDENTITY_FINAL_CHECKS.json').write_text(json.dumps(put,indent=2)+'\n');print(json.dumps({'checks':len(checks),'status':'PASS'}))
