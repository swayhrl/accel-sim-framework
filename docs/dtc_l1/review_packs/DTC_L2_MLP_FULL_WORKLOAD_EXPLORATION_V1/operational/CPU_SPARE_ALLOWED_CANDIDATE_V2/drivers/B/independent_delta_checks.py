import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,copy,types,threading,tempfile,ast
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');B=A/'agents/B/cpu_spare_policy_review_v2'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
op=A/'agents/E/cpu_spare_execution_v2/cpu_owner.py';ep=A/'agents/E/cpu_spare_execution_v2/cpu_extra_strict.py';o=load('B_only_final494_owner',op)
assert sha(op)=='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
assert sha(ep)=='5339e64ffd580e40c93cde4ab0ef9e1cfa92a91045d078a55a93ede37484a5de'
root=P(tempfile.mkdtemp(prefix='B_DELTA_',dir=B));o.R=root
class Frames:
 def __call__(self,pending,claims):return self.res.resources({},True)
frames=Frames();q={'consumed':{'old':{}},'admitted_specs':{'A':'x'}};calls=[];base={'pressure_reasons':['cpu_pressure_full']}
lib=types.SimpleNamespace(eligible_cohort=lambda cfg,q,c,s,claims:True,validate=lambda c,q:None,project_for_candidate=lambda *a,**kw:calls.append(kw)or{'MASKED':True},verify_memory_proof=lambda p:None)
lib.project_for_candidate=lambda *a,**kw:calls.append(kw)or{'additional_cpu_spare_memory_admission_proof':{}}
cfg={'cpu_exception_scope':{'mode':'ALL_ALLOWED_ADMITTED_UNSPENT'},'scope_mode':'ALL_UNSPENT_FUTURE','allowed_cohorts':['A']}
tiny=types.SimpleNamespace(wrapper=lambda *a:base,frames=frames,engine=types.SimpleNamespace(registered=lambda:({}, {},q,{})))
helper=o.frame_helper(tiny,{'context':{'cfg':cfg}},lib);frames.res=types.SimpleNamespace(resources=helper['wrapper'])
ledger=root/'control/qualification_ledger';ledger.mkdir(parents=True);(ledger/'A.INTENT.json').write_text('{}')
assert frames([{'cohort':'A'}],{})is base and not calls
(ledger/'A.INTENT.json').unlink();assert frames([{'cohort':'A'}],{})=={'additional_cpu_spare_memory_admission_proof':{}}and len(calls)==1
checks=['new frame guard excludes existing INTENT witness without masking original pressure; no-INTENT witness still projects']
roles=['library','frontend','owner','extra_strict','joint_padding','joint_io'];old=dict(cfg,canary_qualification_sha256='IMMUTABLE_APPROVAL',**{r+'_sha256':'same'for r in roles});new=copy.deepcopy(old);new['allowed_cohorts']=['A','B']
def resource(*a):return{'admission_decision':{'admission_RAM_budget_bytes':100},'total_projected_additional_RAM_bytes':20}
choose=lambda *a:None
state=types.SimpleNamespace(previous_C=1,protected='UNCHANGED',pending_releases={'credit':'unchanged'})
aging=types.SimpleNamespace(lock=threading.RLock(),state=state,original=choose)
memory=dict(lib=types.SimpleNamespace(ROLES=roles,validate=lambda*c:None),engine=types.SimpleNamespace(registered=lambda:({}, {},q,{}),canonical=lambda c:{}),context={'cfg':old},cfg=old,aging=aging,res=types.SimpleNamespace(resources=resource),new_resources=resource,new_choose=choose)
setattr(sys.modules['__main__'],o.MEMORY,memory)
bad=copy.deepcopy(new);bad['canary_qualification_sha256']='DRIFT'
try:o.update_scope_in_owner(bad,lambda:None)
except AssertionError:pass
else:raise AssertionError('approval drift accepted')
assert memory['context']['cfg']is old and state.previous_C==1
assert o.update_scope_in_owner(new,lambda:None)['new_grants']==0 and memory['context']['cfg']==new and state.previous_C==80 and state.protected=='UNCHANGED'and state.pending_releases=={'credit':'unchanged'}
checks.append('scope append permits allowlist-only change and refuses changed approval before any state mutation; R/release credit unchanged')
pre=next(B.glob('extra_strict_QUALIFIED_PREIMAGE_932d6c0160e7.py'))
assert ast.dump(ast.parse(pre.read_text()),include_attributes=False)==ast.dump(ast.parse(ep.read_text()),include_attributes=False)
out=dict(status='PASS',delta_checks=checks,extra_AST_identical_to_qualified932=True,source_sha256={'owner':sha(op),'extra_strict':sha(ep)},old_six_checks_remain_bound_to_old_sources=True,models_started=0,production_changes=0,new_grants=0,fixture=str(root))
p=B/'FINAL_494_533_DELTA_REVIEW.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'path':str(p),'sha256':sha(p),'status':'PASS'}))
