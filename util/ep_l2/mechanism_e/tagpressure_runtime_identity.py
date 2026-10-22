"""Exact engineering rebind for approved observer env only. No model change.
Uses original frozen identity primitives in isolated function-only namespaces;
never imports runner/registry top-levels or reads trace bodies/binaries.
"""
import ast,copy,hashlib,json
from pathlib import Path
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
LEGACY=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5')
RUN_REF={'path':str(LEGACY/'run.py'),'sha256':'43f65cf89fdbdf81e8786e8b00d2d9be1dfc521c41e386f01ed00fc7708c9060'}
REG_REF={'path':str(LEGACY/'registry.py'),'sha256':'81a31c347bd3c5531eb959569ae7baffbecd5f75c6142a65e1aedbfd05a8808d'}
FORMULA="legacy.content_hash({'ordered_configs':configs,'auxiliary_assets':assets,'environment':spec['environment']}) == identity['runtime_config_sha256']"
FORMULA_AST=ast.dump(ast.parse(FORMULA,mode='eval').body,include_attributes=False)
LIMIT=4*2**20

def require(ok,message):
 if not ok:raise ValueError(message)
def ref(p):
 p=Path(p);require(p.is_file() and p.stat().st_size<=LIMIT,'small config/metadata asset only');return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(r):require(ref(r['path'])['sha256']==r['sha256'],'baseline/ref changed');return json.loads(Path(r['path']).read_text())
def _functions():
 ns={'Path':Path,'hashlib':hashlib,'json':json,'require':require};bodies=[]
 for r,names in ((RUN_REF,{'digest','asset_manifest','content_hash'}),(REG_REF,{'canonical'})):
  require(ref(r['path'])['sha256']==r['sha256'],'original identity primitive source changed')
  nodes=[n for n in ast.parse(Path(r['path']).read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names];require({n.name for n in nodes}==names,'original pure identity helpers absent');bodies.extend(nodes)
 exec(compile(ast.Module(body=bodies,type_ignores=[]),'fixed_original_identity_primitives','exec'),ns)
 return ns

def assert_original_inspector_formula(path=None):
 p=E/'util/ep_l2/mechanism_e/runner.py' if path is None else Path(path)
 require(p.is_file() and p.stat().st_size<=LIMIT,'original inspector source absent')
 matches=[n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.Compare) and ast.dump(n,include_attributes=False)==FORMULA_AST]
 require(len(matches)==1,'original inspector ordered config/assets/environment identity formula changed')
 return hashlib.sha256(FORMULA_AST.encode()).hexdigest()

def payload(spec):
 for rows in (spec['configs'],spec['auxiliary_assets']):
  require(isinstance(rows,list),'ordered asset rows')
  for row in rows:ref(row['path'])
 p=_functions();return {'ordered_configs':p['asset_manifest'](spec['configs'],ordered=True),'auxiliary_assets':p['asset_manifest'](spec['auxiliary_assets']) if spec['auxiliary_assets'] else [],'environment':copy.deepcopy(spec['environment'])}
def runtime_hash(spec):return _functions()['content_hash'](payload(spec))

def baseline_reference(proposed):return {'path':str(E/proposed['baseline_r4_spec']['path']),'sha256':proposed['baseline_r4_spec']['sha256']}
def derive(spec,baseline_ref):
 base=read(baseline_ref);require(spec['configs']==base['configs'] and spec['auxiliary_assets']==base['auxiliary_assets'],'unapproved model config/auxiliary asset change')
 require('EPL2_TAGPRESSURE_DIAG' not in base['environment'],'baseline unexpectedly already r5')
 expected={**base['environment'],'EPL2_TAGPRESSURE_DIAG':'1'};require(spec['environment']==expected,'only approved observer env addition allowed')
 old=payload(base);new=payload(spec);require(old['ordered_configs']==new['ordered_configs'] and old['auxiliary_assets']==new['auxiliary_assets'],'model asset content changed')
 f=_functions();old_hash=f['content_hash'](old);new_hash=f['content_hash'](new)
 require(old_hash==base['identity']['runtime_config_sha256'],'actual baseline runtime hash changed')
 require(new_hash!=old_hash,'new observer env cannot reuse old runtime hash')
 return {'schema':'E2_R5_OBSERVER_ENV_RUNTIME_IDENTITY_REBIND_V1','status':'EXACT_APPROVED_OBSERVER_ENV_ONLY_DERIVED','baseline_spec_ref':copy.deepcopy(baseline_ref),'baseline_runtime_config_sha256':old_hash,'runtime_config_sha256':new_hash,'allowed_environment_addition':{'EPL2_TAGPRESSURE_DIAG':'1'},'baseline_environment':old['environment'],'environment':new['environment'],'ordered_configs':new['ordered_configs'],'auxiliary_assets':new['auxiliary_assets'],'original_formula_ast_sha256':assert_original_inspector_formula(),'original_asset_hash_primitive_refs':[RUN_REF,REG_REF],'scientific_model_asset_bytes_changed':False,'proposal_modified':False}

def verify(spec,baseline_ref,proof=None):
 expected=derive(spec,baseline_ref);require(spec['identity']['runtime_config_sha256']==expected['runtime_config_sha256'],'actual new runtime hash differs from original inspector formula')
 if proof is not None:require(proof==expected,'runtime env rebind proof changed')
 return expected

def frozen_scientific_identity(spec,proposed,proof):
 fields=proposed['frozen_scientific_identity_fields_for_new_condition'];require('runtime_config_sha256' in fields,'approved baseline runtime identity missing')
 require(all(spec['identity'][k]==v for k,v in fields.items() if k!='runtime_config_sha256'),'frozen scientific identity changed')
 expected=verify(spec,baseline_reference(proposed),proof)
 require(fields['runtime_config_sha256']==expected['baseline_runtime_config_sha256'],'proposal baseline runtime identity changed')
 return expected
