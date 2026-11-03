from pathlib import Path
import json,hashlib,re
P=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents');A=P/'A';C=P/'C';sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((A/'MANIFEST.json').read_text());checks=[]
def ck(n,b,d=None):checks.append({'check':n,'PASS':bool(b),'detail':d})
ck('A frozen manifest hash',sha((A/'MANIFEST.json').read_bytes())=='379d5e8dde83e0db93362aed593ce5b4af5431336af167063f20eb018d161312')
ck('All A manifest members byte hash',all(sha((A/x['path']).read_bytes())==x['sha256'] for x in m['files']),{'members':len(m['files'])})
audit=json.loads((C/'INDEPENDENT_SET_AUDIT.json').read_text());expect={(x['program'],x['profile']):x for x in audit['candidates']};matrix=json.loads((A/'CH_CANDIDATE_MATRIX.json').read_text());cs=matrix['candidates'];xmap={'CORE_FOURWAY':'CORE','SUPPLEMENTAL':'SUPPLEMENT','DEFERRED':'DEFERRED'}
ck('A70 unique full identity candidates',len(cs)==70 and len({(x['input_digest'],x['profile']) for x in cs})==70)
ck('A categories equal independent original audit',all(c['category']==xmap[expect[(c['program'],c['profile'])]['classification']] and c['input_digest']==expect[(c['program'],c['profile'])]['input_digest'] for c in cs))
ck('A has zero registrations grants starts UUIDs',not matrix['matrix_registered'] and matrix['models_started']==0 and not matrix['named336_performance_used'] and all(c['runtime_uuid'] is None and c['model_starts']==0 and c['registration_status']=='NOT_REGISTERED' and not c['scientific_execution_authorized'] for c in cs))
l1=json.loads((C/'INDEPENDENT_HARDWARE_FAIRNESS.json').read_text())['CH_DH_P0_all_effective_option_differences'];detail=[]
for c in cs:
 old=json.loads(Path(c['original_parent_spec']['path']).read_text());dh=json.loads(Path(c['original_DH_variant_spec']['path']).read_text());opt=c['effective_options'];target=int(c['profile'][1:])
 dif={k for k in set(old['expected_options'])|set(opt) if old['expected_options'].get(k)!=opt.get(k)}
 d2={k for k in set(dh['expected_options'])|set(opt) if dh['expected_options'].get(k)!=opt.get(k)}
 ok=dif=={'-gpgpu_frfcfs_dram_sched_queue_size'} and opt['-gpgpu_frfcfs_dram_sched_queue_size']==[str(target)] and d2==set(l1)
 bytechecks=[]
 for i,x in enumerate(c['configs']):
  before=Path(old['configs'][i]['path']).read_bytes();after=(A/x['path']).read_bytes();expected=before
  if i==0:expected,n=re.subn(rb'(-gpgpu_frfcfs_dram_sched_queue_size[ \t]+)64\b',lambda m:m.group(1)+str(target).encode(),before);assert n==1
  bytechecks.append(sha(after)==x['sha256'] and after==expected)
 detail.append({'id':c['candidate_id'],'only_FRFCFS_option_changed':dif=={'-gpgpu_frfcfs_dram_sched_queue_size'},'CH_DH_exact_7_L1_differences':d2==set(l1),'config_bytes_exact_patch_and_hash':all(bytechecks),'PASS':ok and all(bytechecks)})
ck('All 70 candidate configs exact single byte patch and downstream matched',all(x['PASS'] for x in detail),{'n':len(detail)})
batch=json.loads((A/'FIRST_BATCH.json').read_text());ck('First16 all fixed core, 8 each two profiles',batch['candidate_count']==16 and set(batch['candidate_ids']).issubset({c['candidate_id'] for c in cs if c['category']=='CORE'}) and len(batch['programs'])==8 and not batch['execution_authorized'] and not batch['registered'])
ck('CPU parser qualification properly limited',bool(json.loads((A/'CPU_ONLY_PARSER_QUALIFICATION.json').read_text())['limitations']), 'Pinned option_parser only and mirrored cache assertions; not full simulator/cache-engine startup qualification.')
resource=json.loads((A/'RESOURCE_AND_ARCHIVE_QUALIFICATION.json').read_text());ck('Resource qualification not execution grant',not resource['execution_qualified'] and resource['model_starts']==0 and len(resource['not_yet_qualified'])>0)
(C/'AGENT_A_INDEPENDENT_REVIEW.json').write_text(json.dumps({'schema':'DTC_STAGE_IIA_AGENT_A_INDEPENDENT_REVIEW_V1','preparation_status':'PASS' if all(x['PASS'] for x in checks) else 'HOLD','execution_status':'NOT_AUTHORIZED','all_checks_PASS':all(x['PASS'] for x in checks),'checks':checks,'candidate_detail':detail,'reviewed_manifest_sha256':sha((A/'MANIFEST.json').read_bytes()),'observations':['No correction required in reviewed frozen package.','777 repeated loop assertions are nine invariant families, not independent scientific observations.','CPU-only option_parser target fixtures do not instantiate all simulator cache semantics.','Six existing exact ratified P0 references are preserved historical rows; no fresh import of PQ/PS/EP/IR/R2.']},indent=2)+'\n');print(json.dumps(checks,indent=2))


