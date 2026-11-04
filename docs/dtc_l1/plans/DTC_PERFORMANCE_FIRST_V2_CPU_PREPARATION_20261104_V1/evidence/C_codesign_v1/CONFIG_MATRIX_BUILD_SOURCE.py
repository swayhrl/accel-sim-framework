from pathlib import Path
from fractions import Fraction
import json,hashlib,shutil,shlex,datetime,os
V=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');O=V/'agents/C_codesign_v1';O.mkdir(parents=True,exist_ok=True);A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');oldroot=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');checks=[]
def rd(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(n,v):(O/n).parent.mkdir(parents=True,exist_ok=True);(O/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def ck(n,b):assert b,n;checks.append(dict(name=n,PASS=True))
# Single immutable V1 snapshot shared with Agent B. No activity/raw/model API.
p=V/'agents/B_mechanisms_v1/FIXED_PROVIDER.json';pb=p.read_bytes();ck('provider11_fixedSHA',hashlib.sha256(pb).hexdigest()=='ebf0e09f8304bd03fa37ea875a59370095321eb0af7f931eadd8ad4298cfd81f');provider=json.loads(pb);ck('upstream_source_qualified',provider['baseline_source_qualified']is True and provider['all_existing_closed_results_qualified']is True and provider['admission_hold_metadata_qualified']is True);ck('snapshot_MF12313',sha(provider['manifest']['path'])==provider['manifest']['sha256']=='12313cdabb29dd31e4fbbca710c862fa9200121fb3c90ce4152029e3955ccaf5');mf=rd(provider['manifest']['path'])
for x in mf['files']:ck('snapshotmember:'+x['name'],sha(x['path'])==x['sha256'])
snap=rd(Path(provider['snapshot'])/'SNAPSHOT.json');ck('frozen11accepted',snap['summary']==provider['summary']and snap['summary']['accepted_new_points']==11);(O/'FIXED_V1_PROVIDER.json').write_bytes(pb);wr('SOURCE_SNAPSHOT_RECEIPT.json',dict(provider_source_path=str(p),provider_sha256=hashlib.sha256(pb).hexdigest(),source_snapshot_manifest=provider['manifest'],observed_utc=provider['observed_utc'],newscience_Root_refs_are_later_native_evidence_not_claimed_in_018d_commit=True,no_live_raw_read=True))
authpath=A/'control/INPUT_AUTHORITY.fixed.json';ck('authority8SHA',sha(authpath)=='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1');auth=rd(authpath);baseline={(r['program'],r['source_cell']):r for x in auth['inputs']for r in x['P0_references']};ck('16P0refs6aliases',len(baseline)==16 and sum(bool(r['legal_prior_P0_alias'])for r in baseline.values())==6)
for r in baseline.values():ck('P0SHA:'+r['program']+r['source_cell'],sha(r['source_RESULT_path'])==r['source_RESULT_sha256']and r['accepted']is True and r['source_profile']=='P0')
basecfg=sorted((oldroot/'DTC/env/DH_P0').glob('config-*.config'));ck('4baseconfigs',len(basecfg)==4)
def parse(paths):
 out={}
 for path in paths:
  tok=[w for token in shlex.split(Path(path).read_text(),comments=True)for w in token.split()];key=None
  for t in tok:
   if t.startswith('-')and len(t)>1 and t[1].isalpha():key=t;out[key]=[]
   else:assert key is not None;out[key].append(t)
 return out
baseopt=parse(basecfg);configinfo={}
for physical in [768,1024]:
 name='PHYS'+str(physical)+'_OOPIB192_TAG64x8';D=O/'configs'/name;D.mkdir(parents=True,exist_ok=True)
 for p in basecfg:(D/p.name).write_bytes(p.read_bytes())
 p=D/'config-3.config';p.write_bytes(p.read_bytes()+('\n# V2 CPU-only planned Physical x OO-PIB combination; no science launch authority.\n-gpgpu_dtc_l1_physical_lines '+str(physical)+'\n-gpgpu_dtc_l1_oo_pib_entries 192\n').encode());paths=sorted(D.glob('config-*.config'));actual=parse(paths);diff={k:dict(from_=baseopt.get(k),to=actual.get(k))for k in baseopt.keys()|actual.keys()if baseopt.get(k)!=actual.get(k)};ck('only2effectiveflags:'+name,set(diff)=={'-gpgpu_dtc_l1_physical_lines','-gpgpu_dtc_l1_oo_pib_entries'}and actual['-gpgpu_dtc_l1_physical_lines']==[str(physical)]and actual['-gpgpu_dtc_l1_oo_pib_entries']==['192']);configinfo[name]=dict(physical_lines=physical,active_OO_PIB_entries=192,effective_shared_lower_create_queue_bound=192,delta=diff,configs=[dict(path=str(p),sha256=sha(p))for p in paths],explicit_effective_options=actual)
wr('CONFIG_SHA_TABLE.json',dict(status='DRAFT_CPU_HEADER_TEST_PENDING',baseline_configs=[dict(path=str(p),sha256=sha(p))for p in basecfg],combinations=configinfo))
v1={(r['input_digest'],r['variant']):r for r in snap['rows']};plans=[];resources=[]
def oldrow(inp,variant):
 r=v1[inp['input_digest'],variant];accepted=r['accepted']is True
 if accepted:ck('V1_RESULTSHA:'+r['cohort'],sha(r['source_RESULT']['path'])==r['source_RESULT']['sha256']and type(r['cycles'])is int and r['cycles']>0)
 old=baseline[inp['program'],'DH']['cycles'];ratio=Fraction(old,r['cycles'])if accepted else None
 return dict(status=r['status'],accepted=accepted,cycles=r['cycles']if accepted else None,performance_direction=('POSITIVE'if ratio>1 else'NEGATIVE'if ratio<1 else'ZERO_EXACT')if accepted else None,S_DH=float(ratio)if ratio else None,source_RESULT=r.get('source_RESULT'),source_role=r.get('source_scientific_role'),uuid=r.get('uuid'),input_digest=inp['input_digest'],same_fixed8=True,not_replaced_by_any_repair_or_named_selection=True)
for x in auth['inputs']:
 inp=x['population'];dh=baseline[inp['program'],'DH'];ch=baseline[inp['program'],'CH']
 for physical in [640,768,1024]:
  for pib in [128,192]:
   if physical==640 and pib==128:kind='FIXED_DH_P0';source=dict(accepted=True,status=dh['source_state'],cycles=dh['cycles'],source_RESULT=dict(path=dh['source_RESULT_path'],sha256=dh['source_RESULT_sha256']),legal_prior_P0_alias=dh['legal_prior_P0_alias'],S_DH=1.0)
   elif pib==128:kind='V1_SINGLE_FACTOR';source=oldrow(inp,'PHYS'+str(physical)+'_TAG64x8')
   elif physical==640:kind='V1_SINGLE_FACTOR';source=oldrow(inp,'OO_PIB192')
   else:kind='V2_UNRUN_COMBINATION';source=dict(accepted=False,status='PLAN_PENDING_AUTHORIZATION_NO_MODEL',cycles=None,S_DH=None)
   resources.append(dict(program=inp['program'],suite=inp['suite'],input_digest=inp['input_digest'],physical_lines=physical,OO_PIB_entries=pib,effective_lower_create_bound=pib,nominal_128B_line_accounting_bytes_per_SM=physical*128,physical_payload_array_or_PPA_certified=False,kind=kind,evidence=source))
 for physical in [768,1024]:
  name='PHYS'+str(physical)+'_OOPIB192_TAG64x8';cfg=configinfo[name];expected=dict(dh['effective_options']);expected['-gpgpu_dtc_l1_physical_lines']=[str(physical)];expected['-gpgpu_dtc_l1_oo_pib_entries']=['192'];ck('all270_exactcombo:'+inp['program']+name,len(expected)==270 and {k for k in expected if expected[k]!=dh['effective_options'][k]}=={'-gpgpu_dtc_l1_physical_lines','-gpgpu_dtc_l1_oo_pib_entries'});phys=oldrow(inp,'PHYS'+str(physical)+'_TAG64x8');pib=oldrow(inp,'OO_PIB192');r=dict(plan_id='PLAN-PERFFIRSTV2-COMBO-'+inp['input_digest'][:16]+'-DH-PHYS'+str(physical)+'-OOPIB192',program=inp['program'],suite=inp['suite'],input_digest=inp['input_digest'],profile=name,cell='DH',downstream_profile='P0',physical_lines=physical,active_OO_PIB_entries=192,effective_lower_create_queue_bound=192,configs=cfg['configs'],expected_effective_options=expected,expected=dh['expected'],input_binding=dh['input_binding'],CH_P0_reference=ch,DH_P0_reference=dh,V1_physical_reference=phys,V1_PIB_reference=pib,new_request=None,new_native_UUID=None,new_scientific_budget_registered=False,model_started=False,performance_cycles=None,S_combo=None,CH_P0_over_newDH=None,J=None,J_status='UNAVAILABLE_NO_NEW_COMBO_RESULT'+(''if phys['accepted']and pib['accepted']else'_AND_SINGLE_FACTOR_PENDING_OR_NONPERFORMANCE'),CPU_status='HEADER_TEST_PENDING',scientific_execution_status='PENDING_NEW_EXPLICIT_AUTHORIZATION',no_Core_change=True,no_Tag_mechanism_dependency=True)
  plans.append(r)
ck('exact16plans8inputs',len(plans)==len({p['plan_id']for p in plans})==16 and len({p['input_digest']for p in plans})==8);wr('DRAFT_C_RESOURCE_CODESIGN_MATRIX.json',dict(schema='DTC_PERFFIRST_V2_PHYSICAL_PIB16_PLAN_DRAFT_V1',status='DRAFT_CPU_HEADER_TEST_PENDING',fixed_core='9eedb3131937748f0492fa83aad37d3691118d70',fixed_framework='02775fd795cde5aae1480d81cee6eb481d0a08f4',authority=dict(path=str(authpath),sha256=sha(authpath)),V1_snapshot=provider['manifest'],resource_matrix_48_rows=resources,candidates=plans,new_model_starts=0,new_scientific_requests=0,new_UUIDs=0,scientific_registration_or_budget=0));wr('CONFIGURATION_CPU_CHECKS.json',dict(status='PASS_CONFIG_ONLY_HEADER_TEST_PENDING',count=len(checks),checks=checks));print('DRAFT16',len(plans),'CONFIG8',[(k,[x['sha256']for x in v['configs']])for k,v in configinfo.items()],'CHECKS',len(checks))
