"""Finite CPU-only Source92 constructor/whole-commandlist RO binding checks."""
import copy,json,os,resource,subprocess,sys,uuid
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0,str(J/'tools'))
from ep_perf_common import *

def main():
    out=J/'control/source92_vector_ro_cpu'/str(uuid.uuid4());out.mkdir(parents=True)
    s=read(J/'cases/EP_PERF_VECTOR4M_F_REF_V1/control/FROZEN_SPEC.json');cert=exact(s['ro_qualification_ref'])
    d=J/'agent_b/bank_ops2_development_v1/extended_runs/c20864a6-3617-4775-a65b-80a954222c14'
    ctor=read(d/'RESULT.json');binary=d/'actual_p2_config_init'
    original=next(r for r in ctor['results'] if r['argv'][0]==str(binary) and '/CTOR_F_G32W8_P1.config' in r['argv'][1])
    need(original['PASS'] and original['returncode']==0,'new actual constructor pass')
    text=(d/'CTOR_F_G32W8_P1.config').read_text()
    for kind in ['manifest','ranges']:
        r=cert[kind+'_ref'];text+='\n-gpgpu_ep_l2_ro_'+kind+' '+r['path']+'\n-gpgpu_ep_l2_ro_'+kind+'_sha256 '+r['sha256']+'\n'
    good=out/'VECTOR_RO.config';good.write_text(text)
    badsha=out/'BAD_SHA.config';badsha.write_text(text+'\n-gpgpu_ep_l2_ro_ranges_sha256 '+'0'*64+'\n')
    cmd=out/'BAD_COUNT_kernelslist.g';cmd.write_bytes(Path(s['trace_entry']).read_bytes()+b'\nkernel-1.traceg\n')
    snapmod=module(ref(J/'agent_c/cpu_consistent_resources_v2.py'),'main_cpu_short_snapshot')
    snap=snapmod.snapshot();writes=snap['cpu_engineering_read_consistency']['own_advertised_remaining_writes']
    decision=snapmod.R.admit(snap,512*M,writes+16*M,policy=exact(s['resource_policy_ref']))
    need(decision['pass_admission'],'finite CPU real-resource admission HOLD')
    cpus=set(os.sched_getaffinity(0))
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:
                status=(p/'status').read_text();a=os.sched_getaffinity(int(p.name))
                if len(a)==1:cpus-=a
            except (OSError,ProcessLookupError):pass
    need(bool(cpus),'one finite CPU slot');cpu=max(cpus)
    def pre():
        os.setsid();os.sched_setaffinity(0,{cpu});os.nice(10)
        resource.setrlimit(resource.RLIMIT_AS,(512*M,)*2);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(4*M,)*2)
    env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',**s['observer_env'])
    checks=[]
    for label,config,command,success in [('EXACT_VECTOR_WHOLE_COMMANDLIST',good,Path(s['trace_entry']),True),('WRONG_RANGE_SHA_REJECTED',badsha,Path(s['trace_entry']),False),('WRONG_COMMAND_POPULATION_REJECTED',good,cmd,False)]:
        args=copy.deepcopy(original['argv']);args[1]=str(config);args[5]=str(command)
        with (out/(label+'.stdout')).open('xb') as stdout,(out/(label+'.stderr')).open('xb') as stderr:
            p=subprocess.run(args,stdout=stdout,stderr=stderr,env=env,preexec_fn=pre,timeout=30)
        need((p.returncode==0)==success,'actual source92 CPU loader control failed '+label)
        wire=(out/(label+'.stdout')).read_text()
        if success:need(wire.count('RO_bound_whole_commandlist=1')==2 and 'GPU_OBJECTS=0|Trace_body_reads=0|epochs_started=0|cycles=0|requests=0' in wire,'actual complete CPU-only loader population')
        checks.append(dict(label=label,argv=args,returncode=p.returncode,expected_success=success,PASS=True,stdout_ref=ref(out/(label+'.stdout')),stderr_ref=ref(out/(label+'.stderr'))))
    receipt=dict(schema='EP_SOURCE92_EXACT_VECTOR_WHOLE_COMMANDLIST_RO_CPU_V1',status='ACTUAL_SOURCE92_VECTOR_RO_POSITIVE_TWO_NEGATIVE_CPU_PASS_NOT_APPLICATION',source_identity=ctor['source_identity'],input_identity_sha256=s['input_identity_sha256'],
        old_RO_facts_reused_not_body_rescanned=True,old_qualification_ref=s['ro_qualification_ref'],manifest_ref=cert['manifest_ref'],ranges_ref=cert['ranges_ref'],exact_new_constructor_binary_ref=ref(binary),exact_constructor_build_evidence_ref=ref(d/'RESULT.json'),
        whole_commandlist_sha256=sha(s['trace_entry']),CPU_affinity=cpu,RSS_AS_limit_bytes=512*M,resource_snapshot=snap,resource_admission=decision,checks=checks,full_ELF_or_application_starts=0,Source_keep=True)
    r=put(out/'RESULT.json',receipt,True)
    put(J/'control/SOURCE92_VECTOR_RO_CPU_RESULT_REF.json',r,True)
    print(json.dumps(dict(receipt_ref=r,checks=3,model_starts=0)))

if __name__=='__main__':main()
