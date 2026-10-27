"""Pure future template preflight; never registers, writes production, or launches.
Adds guards outside the unchanged 21-source campaign contract: signed partition
credit representability and canonical uniform profile identity across frozen35.
"""
import pathlib,json,hashlib,importlib.util,copy
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');INT_MAX=2147483647;MAX_FRFCFS=INT_MAX-191
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def require(v,msg):
 if not v:raise ValueError(msg)
def safe_parameters(parameters):
 gen=load('future_only_unchanged_generator',R/'tools/l2_config_generator.py');p=gen.normalize(parameters);require(p['frfcfs']<=MAX_FRFCFS,'SIGNED_PARTITION_SHARED_CREDIT_BOUND: F+191 must fit Core int m_shared_credit_limit');return p
def profile_name(parameters):
 p=safe_parameters(parameters);keys=[('entries','E'),('merge','M'),('miss_queue','Q'),('frfcfs','F')];base=dict(entries=192,merge=4,miss_queue=32,frfcfs=64);return '_'.join(prefix+str(p[k])for k,prefix in keys if p[k]!=base[k])or'P0'
def validate_profile_identity(parameters,requested_profile=None,existing_vectors=None):
 p=safe_parameters(parameters);name=profile_name(p);require(requested_profile in[None,name],'PROFILE_NAME_PARAMETER_VECTOR_MISMATCH')
 for prior,vector in(existing_vectors or{}).items():
  if prior==name:require(safe_parameters(vector.get('parameters',vector))==p,'EXISTING_PROFILE_NAME_VECTOR_COLLISION')
 return name,p
def compile_uniform(parameters,cell,scope,existing_vectors=None,requested_profile=None):
 require(cell in['CH','DH'],'unsupported cell');name,p=validate_profile_identity(parameters,requested_profile,existing_vectors);points=scope['points'];ids=sorted({x['input_digest']for x in points});require(scope['frozen_input_count']==len(ids)==35,'exact frozen35 domain required');require(len({d[:16]for d in ids})==35,'cohort prefix collision');gen=load('future_uniform_unchanged_generator',R/'tools/l2_config_generator.py');changed={k for k in p if p[k]!=gen.BASE[k]};allowed_pairs=[{'entries','merge'},{'entries','miss_queue'},{'entries','frfcfs'},{'merge','miss_queue'},{'merge','frfcfs'}];require(len(changed)!=2 or changed in allowed_pairs,'pair not in predeclared adaptive contract');bases={}
 for d in ids:
  matches=[x for x in points if x['input_digest']==d and x['cell']==cell and x['profile']=='P0'];require(len(matches)==1,'missing/duplicate samecell P0 base');bases[d]=matches[0]
 result=[];shared_texts=None;transforms=[]
 for d in ids:
  b=bases[d];basepath=R/'control/specs'/(b['cohort']+'.json');base=read(basepath);require(base['cohort']==b['cohort']and base['input_digest']==d and base['cell']==cell,'frozen base identity mismatch');texts=[]
  for c in base['configs']:require(sha(c['path'])==c['sha256'],'base config source SHA drift');texts.append(P(c['path']).read_text())
  after,manifest=gen.generate(texts,p)
  if shared_texts is None:shared_texts=after
  else:require(after==shared_texts,'same uniform profile would create per-input configuration drift')
  before=gen.effective_options(texts);effective=manifest['effective_options'];require(all(effective[k]==v for k,v in before.items()if k not in[gen.L2,gen.FR]),'non-target clock/DTC/hash option changed');require(manifest['logical_resource_cost']['l2_data_bytes']==10485760,'cache capacity drift');c='E2-DTCL2MLP-'+d[:16]+'-'+cell+'-'+name+'-V1';reuse=any(x['cohort']==c for x in points)
  if reuse:
   prior=read(R/'control/specs'/(c+'.json'));prior_texts=[]
   for cfg in prior['configs']:require(sha(cfg['path'])==cfg['sha256'],'reuse config SHA drift');prior_texts.append(P(cfg['path']).read_text())
   require(gen.effective_options(prior_texts)==effective,'existing named cohort configuration vector collision');require(all(prior[k]==base[k]for k in['expected','input_digest','cell','core_commit','framework_commit','original_environment'])and prior['native_simulator_argv'][:3]==base['native_simulator_argv'][:3],'reuse complete-input/build identity mismatch')
  result.append(dict(cohort=c,input_digest=d,cell=cell,profile=name,uniform_parameters=p,program=b['program'],suite=b['suite'],expected_complete_input=copy.deepcopy(base['expected']),base_spec_path=str(basepath),base_spec_sha256=sha(basepath),original_trace_argv=base['native_simulator_argv'][:3],immutable_input_identity_sha256=hashlib.sha256(json.dumps({k:v for k,v in base.items()if k not in['cohort','profile','downstream_profile','configs','expected_options','native_simulator_argv','host_cpu']},sort_keys=True).encode()).hexdigest(),already_registered_exact_cohort=reuse));transforms.append(manifest)
 return dict(schema='FUTURE_UNIFORM_FROZEN35_PARAMETER_TEMPLATE_V1',status='CPU_CANDIDATE_NOT_REGISTERED_NOT_ADMISSION_READY',cell=cell,profile=name,parameters=p,input_count=35,points=result,ordered_config_texts=shared_texts,transform=transforms[0],new_cell_count=sum(not x['already_registered_exact_cohort']for x in result),requires_whole_suite_evidence_and_coordinator_grant=True,requires_independent_host_RSS_AS_forecast_and_fresh_admission=True,logical_slot_cost_not_physical_area_or_RSS=True,FRFCFS_and_shared_partition_credit_are_coupled=True,model_starts=0)
