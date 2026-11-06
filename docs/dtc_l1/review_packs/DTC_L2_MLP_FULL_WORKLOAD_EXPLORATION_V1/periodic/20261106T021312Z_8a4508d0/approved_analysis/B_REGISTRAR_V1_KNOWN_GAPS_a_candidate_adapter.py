"""Read-only exact adapter for A's sealed CH AD1 candidate construction schema.

It returns JSON objects; caller may save them only to its own candidate folder.
No grant or selection is inferred from this construction certificate.
"""
import pathlib,json,hashlib,copy
P=pathlib.Path
A_MANIFEST_SHA='4638547d2fdac29f8e6cd3bd38033e2e6e55c6f377b57a823148537964dd28ff'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def normalize(candidate_root,native_root):
 d=P(candidate_root);root=P(native_root);manifestpath=d/'MANIFEST.json';assert sha(manifestpath)==A_MANIFEST_SHA
 manifest=read(manifestpath);assert manifest['schema']=='AD1_CH70_INDEPENDENT_PENDING_CANDIDATE_MANIFEST_V1'and manifest['status']=='PENDING_NOT_REGISTERED_NOT_SELECTED'and manifest['cohort_count']==70 and manifest['unique_inputs']==35
 members=[]
 for entry in manifest['members']:
  path=d/entry['path'];assert path.resolve().is_relative_to(d.resolve())and sha(path)==entry['sha256']
  members.append(dict(path=str(path),sha256=entry['sha256']))
 members.append(dict(path=str(manifestpath),sha256=A_MANIFEST_SHA))
 index=read(d/'CANDIDATE_INDEX.json');assert index['schema']=='AD1_TWO_UNIFORM_CH_BATCH_CANDIDATES_V1'and index['status']=='PENDING_NOT_REGISTERED_NOT_SELECTED'and index['no_current_profile_selection']is True and index['new_grants']==index['models_started']==0
 scopepath=d/'contracts/SCOPE_INITIAL.json';scope=read(scopepath);digests=sorted({p['input_digest']for p in scope['points']});assert len(scope['points'])==350 and len(digests)==35
 bindings=read(d/'SOURCE_AND_BUILD_BINDINGS.json')
 for p,h in bindings['source_pins'].items():assert sha(p)==h
 # The sealed parent snapshot is science provenance; current parent RSS is not
 # permanently pinned. Config/build/input sources remain individually pinned.
 rows=[]
 for point in index['points']:
  assert point['scientific_role']=='ADAPTIVE_PARAMETER_PERFORMANCE_TRIAL'and point['baseline_reference_status']=='UNRESOLVED'
  assert sha(point['spec_path'])==point['spec_sha256']and sha(point['lineage_path'])==point['lineage_sha256']
  lineage=read(point['lineage_path']);spec=read(point['spec_path']);assert spec['adaptive_trial_lineage']==lineage
  basepath=P(lineage['parent_spec_snapshot_path']);assert sha(basepath)==lineage['parent_spec_sha256'];base=read(basepath)
  assert base['cohort']==lineage['parent_cohort']and spec['input_digest']==base['input_digest']==point['input_digest']and spec['cell']==point['cell']=='CH'
  rows.append(dict(cohort=point['cohort'],input_digest=point['input_digest'],cell='CH',profile=point['profile'],parameters=lineage['uniform_parameters'],role=point['scientific_role'],candidate_set_id='A_SEALED_CH70_AD1_V1',spec_path=point['spec_path'],spec_sha256=point['spec_sha256'],base_spec_path=str(basepath),base_spec_sha256=lineage['parent_spec_sha256'],base_cohort=lineage['parent_cohort'],original_candidate_lineage=copy.deepcopy(lineage)))
 assert len(rows)==70 and len({r['cohort']for r in rows})==70
 for profile in ['F128','F256']:
  selected=[r for r in rows if r['profile']==profile];assert len(selected)==35 and {r['input_digest']for r in selected}==set(digests)
 gates=[]
 for b in index['batches']:
  assert sha(b['path'])==b['sha256'];batch=read(b['path']);gates.append(dict(batch_id=batch['batch_id'],path=b['path'],sha256=b['sha256'],activation_gate=batch['activation_gate']))
 return dict(schema='NORMALIZED_ADAPTIVE_CH_AD1_CANDIDATES_V1',request='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1',status='PENDING_NOT_REGISTERED_NOT_SELECTED',candidate_set_id='A_SEALED_CH70_AD1_V1',source_A_manifest_sha256=A_MANIFEST_SHA,frozen_scope_path=str(scopepath),frozen_scope_sha256=sha(scopepath),frozen_input_digests=digests,candidate_batch_activation_gates=gates,initial350_matrix_sha256=sha(root/'control/MATRIX_CURRENT.json'),rows=rows),dict(status='PENDING_NOT_REGISTERED_NOT_SELECTED',request='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1',source_A_manifest_sha256=A_MANIFEST_SHA,members=members,construction_only_not_registration_approval=True)
