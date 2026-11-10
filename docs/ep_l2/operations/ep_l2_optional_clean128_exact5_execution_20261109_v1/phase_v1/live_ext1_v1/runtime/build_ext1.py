#!/usr/bin/env python3
"""Prepare the one authorized Stencil EXT1 point without registry or model writes.

Run on 174-new. The old exact5 Host and its closed cases remain byte identical.
"""
import copy
import hashlib
import json
import os
from pathlib import Path

P = Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
OLD = ROOT/'runtime/host_stencil_bound_v2'
HOST = ROOT/'runtime/host_stencil_ext1_bound_v1'
REQ = 'EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CASE = 'EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
OLD_CASE = 'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'
OLD_REQ = 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'
NATIVE = P('/root/data/ep_l2_dtc_l1_native_v2')
CONTROL = ROOT/'control'
EXT2 = ROOT/'cases'/OLD_CASE/'control/FROZEN_SPEC.json'
AUTH = CONTROL/'EXT1_USER_AUTHORIZATION.json'

def need(x, msg):
    if not x: raise RuntimeError(msg)
def sha(p):
    h=hashlib.sha256()
    with P(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def once(p,data):
    p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():need(p.read_bytes()==data,'immutable file drift '+str(p))
    else:
        with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    return ref(p)
def jonce(p,x):return once(p,enc(x))
def replace_exact(t,old,new):
    need(old in t,'missing replacement '+old)
    return t.replace(old,new)

def main():
    old=json.loads(EXT2.read_bytes())
    need(sha(EXT2)=='34559c8f77cdb5ddd51dbdbed5eef65ef6bb426e233ff91fd2e023cd2c5f442a','EXT2 fixed Spec drift')
    reg=json.loads((NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())
    rows=reg['registered_future_requests']
    need(REQ not in rows and all(CASE not in (q.get('admitted_specs') if isinstance(q.get('admitted_specs'),dict) else {}) and CASE not in (q.get('consumed') if isinstance(q.get('consumed'),dict) else {}) for q in rows.values()),'EXT1 already registered')
    need(json.loads((CONTROL/'DISPATCH_CLAIMS.json').read_bytes())['claims']=={},'shared claims not empty')
    for req in ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',OLD_REQ):
        q=rows[req];need(q['remaining']==0 and len(q['consumed'])==q['budget'] and all(z['state']=='CLOSED_ACCEPTED' for z in q['consumed'].values()),'old five not all accepted')
    a={
      'schema':'EP_L2_STENCIL_EXT1_ONE_POINT_USER_AUTHORIZATION_V1',
      'goal':'EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_EXECUTION_V1',
      'request_id':REQ,'cohort':CASE,'explicit_user_approval':True,
      'approved_total_launches':1,'automatic_retry':False,'refund':False,'source_keep':True,
      'approval_quote':'授权',
      'review_commit':'680b20f5ee2dc3f5cd335adf005c7235ebc5abce',
      'record_commit':'44b58f5d8e7e46c88351ad43dc0b6b141766c082',
      'fixed_ext2_spec_ref':ref(EXT2),'source_identity':old['source_identity'],
      'input_identity_sha256':old['input_identity_sha256'],
      'families':[{'request_id':REQ,'allowed_cohorts':[CASE],'approved_launches':1}],
    }
    authref=jonce(AUTH,a)
    HOST.mkdir(parents=True,exist_ok=True)
    modified={
      'ep_perf_common_v2.py': lambda t:replace_exact(t,"GOAL = '"+OLD_REQ+"'","GOAL = '"+REQ+"'"),
      'ep_perf_frontend.py': lambda t:replace_exact(t,"('EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1', '"+OLD_CASE+"')","('"+CASE+"',)"),
      'ep_perf_native_wv_modes_draft.py': lambda t:t,
      'ep_perf_postprocess.py': lambda t:t,
      'ep_perf_archive.py':lambda t:replace_exact(t,'ep_l2_optional_clean128_exact5_20261109_v1/stencil','ep_l2_optional_clean128_stencil_ext1_20261110_v1'),
      'resources_b1.py':lambda t:replace_exact(t,"REQUEST='"+OLD_REQ+"'","REQUEST='"+REQ+"'"),
      'runtime_monitor_schema_v4_strict.py':lambda t:t,
      'native_b1':lambda t:replace_exact(t,'host_stencil_bound_v2/ep_perf_frontend.py','host_stencil_ext1_bound_v1/ep_perf_frontend.py'),
    }
    for name,func in modified.items():
        t=func((OLD/name).read_text())
        if name=='ep_perf_native_wv_modes_draft.py':
            t=replace_exact(t,"('EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1', '"+OLD_CASE+"')","('"+CASE+"',)")
            t=replace_exact(t,"auth['approved_total_launches'] == 5","auth['approved_total_launches'] == 1")
            t=replace_exact(t,"auth['user_request_ref'] == ref(ROOT / 'control/USER_REQUEST.txt')","auth['cohort'] == case and auth['request_id'] == GOAL")
            t=replace_exact(t,"ROOT/'control/NATIVE_ENTRY_ROUTE_EXACT5.json'","ROOT/'control/NATIVE_ENTRY_ROUTE_EXT1.json'")
        once(HOST/name,t.encode())
    # The new mode validator checks only the delta from the accepted EXT2 identity.
    mode='''import hashlib,json\nfrom pathlib import Path\nP=Path\nEXT2=P("'''+str(EXT2)+'''")\nPIN="34559c8f77cdb5ddd51dbdbed5eef65ef6bb426e233ff91fd2e023cd2c5f442a"\nCASE="'''+CASE+'''"\nREQ="'''+REQ+'''"\ndef validate_static(s,candidate=False):\n assert hashlib.sha256(EXT2.read_bytes()).hexdigest()==PIN\n b=json.loads(EXT2.read_bytes())\n assert s['cohort']==CASE and s['science_request_id']==REQ and s['victim_extension']==1\n assert s['source_identity']==b['source_identity'] and s['input_identity_sha256']==b['input_identity_sha256']\n assert s['mode']==b['mode']=='WV_ZERO_RO' and s['T'] is s['M'] is False\n assert s['geometry']==b['geometry'] and s['limits']==b['limits']\n assert s['expected_instructions']==b['expected_instructions'] and s['expected_CTA']==b['expected_CTA']\n assert s['expected_kernel_launches']==b['expected_kernel_launches'] and s['expected_kernel_scopes']==b['expected_kernel_scopes']\n assert s['all_unique_kernel_members']==b['all_unique_kernel_members'] and s['command_count']==b['command_count']\n x=dict(b['expected_effective_options']);x['-gpgpu_ep_l2_victim_extension']='1'\n assert s['expected_effective_options']==x and len(x)==283\n assert s['exact_config_canonical_sha256']=='36b9d132a37645c2f6b3f68522fbfca39ed1f0ff091aab0b93d5668fb1738af9'\n assert s['application_budget']==s['approved_launches']==1 and s['automatic_retry'] is s['refund'] is False\n assert s['source_keep'] is True\n return {'status':'EXT1_SOURCE5_EXACT_DELTA_PASS_NO_START','launch_permission':False}\n'''
    mode_ref=once(ROOT/'runtime/ext1_mode_contract.py',mode.encode())
    guard='''import hashlib,json\nfrom pathlib import Path\nP=Path\ndef sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()\ndef validate_current(p):\n r=json.loads(P(p).read_bytes())\n assert r['request_ids']==['''+repr(REQ)+'''] and r['exact_cohorts']==['''+repr(CASE)+''']\n assert r['guard_module_ref']=={'path':str(P(__file__).resolve()),'sha256':sha(__file__)}\n assert r['Main_user_authorization_ref']['sha256']==sha(r['Main_user_authorization_ref']['path'])\n a=json.loads(P(r['Main_user_authorization_ref']['path']).read_bytes())\n assert a['explicit_user_approval'] and a['approved_total_launches']==1 and a['request_id']==r['request_ids'][0]\n for k in ('old_route_ref','old_global_ref','owned_prefix_ref'):\n  assert sha(r[k]['path'])==r[k]['sha256']\n old=json.loads(P(r['old_route_ref']['path']).read_bytes())\n assert old['request_ids']==['EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1','EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1']\n assert P(r['old_global_ref']['path']).read_bytes()==P(old['owned_prefix_ref']['path']).read_bytes()+P(old['global_preimage_ref']['path']).read_bytes()\n prefix=P(r['owned_prefix_ref']['path']).read_bytes()\n assert prefix.count(b'experiment:EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1')==1\n assert P(r['global_shared_native_path']).read_bytes()==prefix+P(r['old_global_ref']['path']).read_bytes()\n entry=r['entry_refs'][r['request_ids'][0]]\n assert sha(entry['path'])==entry['sha256'] and b'EP_FULL_PERF_NATIVE_ENTRY=1' in P(entry['path']).read_bytes()\n return {'status':'EXT1_ADDITIVE_NATIVE_ROUTE_PASS','global_sha256':sha(r['global_shared_native_path'])}\n'''
    guardref=once(ROOT/'runtime/native_route_guard_ext1.py',guard.encode())
    base=HOST/'resources_b1.py';base_ref=ref(base)
    resource='''"""Own EXT1 resource mapping. Retain all foreign published writes."""\nimport hashlib,importlib.util,json\nfrom pathlib import Path\nP=Path\nBASE=P("'''+str(base)+'''")\nPIN="'''+base_ref['sha256']+'''"\nREG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')\nEPOCH=P('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')\nOLD=('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1','''+repr(OLD_REQ)+''')\ndef impl():\n assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PIN\n s=importlib.util.spec_from_file_location('ext1_base_resources',BASE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m\ndef snapshot():\n m=impl();s=m.snapshot();raw=REG.read_bytes();e=json.loads(EPOCH.read_bytes())\n if hashlib.sha256(raw).hexdigest()!=s.get('registry_sha256') or e['native_registry_sha256']!=s.get('registry_sha256'):\n  s['foreign_metadata_errors'].append('EXT1 registry/epoch race');return s\n reg=json.loads(raw)['registered_future_requests'];claims=json.loads((P("'''+str(CONTROL)+'''/DISPATCH_CLAIMS.json")).read_bytes())['claims']\n if any(c.get('request') not in ("'''+REQ+'''",)+OLD or c.get('cohort')!=name for name,c in claims.items()):\n  s['foreign_metadata_errors'].append('unknown shared claim owner');return s\n live=s.get('actual_loader_aware_models',[])\n if live:return s\n for req in OLD:\n  q=reg[req];rows=q['consumed']\n  if not(q['remaining']==0 and q['reserved_write_bytes']==0 and len(rows)==q['budget'] and all(r['state']=='CLOSED_ACCEPTED' for r in rows.values())):return s\n  if any(c.get('request')==req for c in claims.values()):return s\n  reason='unmapped active foreign RAM owner '+req\n  if reason in s['foreign_metadata_errors']:s['foreign_metadata_errors'].remove(reason)\n s['ext1_terminal_reconciliation']={'closed_old_requests':list(OLD),'registry_sha256':s['registry_sha256'],'foreign_write_entries_unchanged':True,'no_live_models':True}\n return s\ndef admit(s,additional,writes,policy):return impl().admit(s,additional,writes,policy)\n'''
    resource_ref=once(HOST/'resources_ext1.py',resource.encode())
    # Route preimage remains a separate immutable file; old installed route is not altered here.
    global_path=NATIVE/'bin/native';global_bytes=global_path.read_bytes()
    oldroute=CONTROL/'NATIVE_ENTRY_ROUTE_EXACT5.json'
    oldr=json.loads(oldroute.read_bytes())
    need(global_bytes==P(oldr['owned_prefix_ref']['path']).read_bytes()+P(oldr['global_preimage_ref']['path']).read_bytes(),'installed old route drift')
    oldglobal=CONTROL/'EXT1_OLD_GLOBAL_NATIVE.bin';once(oldglobal,global_bytes)
    prefix=("#!/bin/sh\nset -eu\n# EP-L2 Main authorized Stencil EXT1 one point.\n"
            "if [ \"$#\" -eq 5 ] && [ \"$1\" = experiment ] && [ \"$4\" = --project ] && [ \"$5\" = EP_L2 ]; then\n"
            " case \"$1:$3\" in\n  experiment:"+CASE+")\n   exec "+str(HOST/'native_b1')+" \"$@\"\n   ;;\n esac\nfi\n").encode()
    prefixref=once(CONTROL/'NATIVE_OWNED_PREFIX_EXT1.bin',prefix)
    route={'schema':'EP_L2_STENCIL_EXT1_ADDITIVE_NATIVE_ROUTE_V1','approved_by':'EP-L2 Main','request_ids':[REQ],
       'exact_cohorts':[CASE],'entry_refs':{REQ:ref(HOST/'native_b1')},'Main_user_authorization_ref':authref,
       'guard_module_ref':guardref,'old_route_ref':ref(oldroute),'old_global_ref':ref(oldglobal),
       'owned_prefix_ref':prefixref,'global_shared_native_path':str(global_path),'source_keep':True}
    routeref=jonce(CONTROL/'NATIVE_ENTRY_ROUTE_EXT1.json',route)
    # Formal one-point Spec; old source/input membership is inherited exactly.
    casepath=ROOT/'cases'/CASE;overlay=casepath/'env/config-5.config'
    overlayref=once(overlay,b'-gpgpu_ep_l2_victim_extension 1\n')
    need(overlayref['sha256']=='fef517887bdccd7b48d6803d14e371ee3aa2d68ce39f7577ccd0328a007fe7c5','overlay hash differs from reviewed candidate')
    spec=copy.deepcopy(old);spec.update(cohort=CASE,science_request_id=REQ,victim_extension=1,
      proposal_point_id='EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1',
      exact_config_canonical_sha256='36b9d132a37645c2f6b3f68522fbfca39ed1f0ff091aab0b93d5668fb1738af9',
      authorization_status='USER_AUTHORIZED_NEW_EXT1_ONE_START',Main_scientific_launch_authorization=authref,
      status='MAIN_BOUND_EXT1_SOURCE5_PENDING_NATIVE_ROUTE_AND_REGISTRY',
      native_entry_ref=ref(HOST/'native_b1'),native_route_guard_ref=guardref,
      mode_contract_ref=mode_ref,host_common_ref=ref(HOST/'ep_perf_common_v2.py'),
      host_engine_ref=ref(HOST/'ep_perf_native_wv_modes_draft.py'),
      postprocess_module_ref=ref(HOST/'ep_perf_postprocess.py'),archive_module_ref=ref(HOST/'ep_perf_archive.py'),
      resource_module_ref=resource_ref)
    spec['expected_effective_options']['-gpgpu_ep_l2_victim_extension']='1'
    spec['ordered_configs'][-1]=overlayref
    spec['pinned_files'][str(overlay)]=overlayref['sha256']
    for p in (HOST/'ep_perf_common_v2.py',HOST/'ep_perf_frontend.py',HOST/'ep_perf_native_wv_modes_draft.py',HOST/'ep_perf_postprocess.py',HOST/'ep_perf_archive.py',HOST/'resources_b1.py',HOST/'resources_ext1.py',HOST/'runtime_monitor_schema_v4_strict.py',HOST/'native_b1',ROOT/'runtime/ext1_mode_contract.py',ROOT/'runtime/native_route_guard_ext1.py'):
        spec['pinned_files'][str(p)]=sha(p)
    oldq=json.loads(P(old['host_qualification_ref']['path']).read_bytes())
    q=copy.deepcopy(oldq);q['schema']='EP_L2_STENCIL_EXT1_HOST_QUALIFICATION_V1';q['cohorts_qualified']=[CASE]
    q['modules']=[ref(P(x['path'])) for x in oldq['modules'] if 'host_stencil_bound_v2' not in x['path'] and 'exact5_mode_contract' not in x['path'] and 'native_route_guard_exact5' not in x['path']]
    q['modules'] += [ref(p) for p in (HOST/'ep_perf_common_v2.py',HOST/'ep_perf_frontend.py',HOST/'ep_perf_native_wv_modes_draft.py',HOST/'ep_perf_postprocess.py',HOST/'ep_perf_archive.py',HOST/'resources_b1.py',HOST/'resources_ext1.py',HOST/'runtime_monitor_schema_v4_strict.py',HOST/'native_b1',ROOT/'runtime/ext1_mode_contract.py',ROOT/'runtime/native_route_guard_ext1.py')]
    spec['host_qualification_ref']=jonce(ROOT/'documents/HOST_QUALIFICATION_EXT1_STENCIL.json',q)
    bind={'schema':'EP_L2_EXT1_MAIN_ENGINEERING_BINDING_V1','authorization_ref':authref,'host_qualification_ref':spec['host_qualification_ref'],
          'old_ext2_spec_ref':ref(EXT2),'route_candidate_ref':routeref,'source_keep':True,'models_started':False}
    spec['Main_engineering_binding_ref']=jonce(ROOT/'documents/MAIN_ENGINEERING_BINDING_EXT1.json',bind)
    specpath=casepath/'control/FROZEN_SPEC.json'
    specref=jonce(specpath,spec)
    print(json.dumps({'status':'EXT1_FORMAL_SPEC_PREPARED_NO_REGISTRY_NO_START','spec_ref':specref,'route_ref':routeref,'new_global_sha256':hashlib.sha256(prefix+global_bytes).hexdigest()}))

if __name__=='__main__':main()
