"""Finite D offline input audit. No simulator, GPU, production edit or E lease.

Uses ONLY pure parsing functions from the exact E review commit. The E CLI,
Registry and resource/launch functions are not imported or invoked. A failed or
unfinished candidate cannot become an input registration. Formal acceptance
and any replacement decision remain E's responsibility.
"""
import ast
from collections import Counter
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import resource
import subprocess
import time

REPO=Path(__file__).resolve().parents[3]
DOC=REPO/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
OUT=DOC/'input_suitability_20261020_r1'
E='69301fe9d336af4a9638099461f6823b0c1252ba'
NATIVE_FW='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
TOOL='util/ep_l2/ft_lane5/atomic_trace_scope.py'
STRICT='util/ep_l2/ft_lane5/native_legacy_trace_proof.py'

def git(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=REPO)
def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def decoder():
    """Extract unmodified pure E definitions; never import its mutating CLI."""
    source=git(E,TOOL);strict=git(E,STRICT)
    ns=dict(Counter=Counter,Path=Path,math=math,re=re,io=io,gzip=gzip,hashlib=hashlib)
    names={'require','integer','instruction','inspect_lines','HashReader','kernel'}
    tree=ast.parse(source)
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    nodes += [n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['MAPS','GLOBAL','SHARED'] for t in n.targets)]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),E+':'+TOOL,'exec'),ns)
    t=ast.parse(strict)
    nodes=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='native_fields']
    nodes += [n for n in t.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='MEMORY' for v in n.targets)]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),E+':'+STRICT,'exec'),ns)
    sources={TOOL:sha(source),STRICT:sha(strict)};maps={}
    for binary,arch in ns['MAPS'].items():
        p=f'gpu-simulator/ISA_Def/{arch}_opcode.h';b=git(NATIVE_FW,p);sources[p]=sha(b)
        text=re.sub(r'/\*.*?\*/','',b.decode(),flags=re.S)
        text='\n'.join(s.split('//')[0] for s in text.splitlines())
        pairs=re.findall(r'\{\s*"([A-Z0-9_]+)"\s*,\s*OpcodeChar\(\s*(OP_[A-Z0-9_]+)',text)
        if not pairs:raise ValueError('missing frozen native opcode map')
        maps[binary]=dict(pairs)
    return ns,maps,sources

def audit(candidate,ns,maps,deadline):
    start=time.monotonic();entry=Path(candidate['entry'])
    result={'workload':candidate['workload'],'status':'INCOMPLETE_NOT_ELIGIBLE',
      'E_scientific_acceptance':False,'registration_changed':False,'files':[],
      'first_rejected_record':None,'expected_full_instructions':candidate['expected_full_application_instructions'],
      'commandlist_path':str(entry),'historical_expected_tree_hash':candidate['published_trace_tree_sha256'],
      'hash_scope':'body SHA from existing D preregistered candidate manifest; original ROUND1 tree hash differs from native composite hash'}
    last={};original=ns['instruction'];extra=Counter()
    def guard():
        if time.monotonic()>=deadline:raise TimeoutError('bounded offline analysis deadline')
    def wrapped(line,version,lineinfo,block,warp,opcodes):
        last.update(line=line,version=version,lineinfo=lineinfo,block=block,warp=warp)
        value=original(line,version,lineinfo,block,warp,opcodes)
        pc,mask,op,extended=ns['native_fields'](line,version,lineinfo)
        if extended:extra[op]+=1
        # A full32 list with a partial active mask can also look like n+imm
        # when n=31. Record it as ambiguous rather than grant a D clearance.
        w=line.split();pos=(4 if version<3 else 0)+lineinfo+2
        nd=int(w[pos]);pos+=1+nd;pos+=1;src=int(w[pos]);pos+=1+src
        mem=int(w[pos]);pos+=1
        if mem and int(w[pos])==0:
            fields=w[pos+1:]
            if 0<mask<0xffffffff and len(fields)==32:
                raise ValueError('PARTIAL_MASK_FULL32_LIST_IS_AMBIGUOUS_NO_D_SCOPE_CLEARANCE')
        return value
    try:
        commands=entry.read_bytes();result['commandlist_sha256']=sha(commands)
        if result['commandlist_sha256']!=candidate['commandlist_sha256']:
            raise ValueError('existing command list identity changed')
        names=[s.strip() for s in commands.decode().splitlines() if s.strip().startswith('kernel')]
        expected={Path(r['path']).name:r for r in candidate['bodies']}
        if len(names)!=candidate['body_count'] or set(names)!=set(expected):raise ValueError('incomplete declared bodies')
        ns['instruction']=wrapped
        for name in names:
            guard();p=entry.parent/name;last.clear()
            parsed,binding=ns['kernel'](p,maps,guard)
            if binding!={k:expected[name][k] for k in ['sha256','bytes']}:
                raise ValueError('full candidate body identity changed')
            if not parsed['atomic_absence']:raise ValueError('native atomic opcode present requires separate qualification')
            result['files'].append(dict(name=name,**binding,**parsed))
        total=sum(r['active_lane_instruction_records'] for r in result['files'])
        result['full_active_lane_instruction_records']=total
        if total!=candidate['expected_full_application_instructions']:
            raise ValueError('complete input instruction count differs from existing baseline')
        manifest=[{'name':entry.name,'sha256':sha(commands),'bytes':len(commands)}]+[
            {k:r[k] for k in ['name','sha256','bytes']} for r in result['files']]
        result['trace_content_manifest']=sorted(manifest,key=lambda r:r['name'])
        result['trace_content_sha256']=sha(json.dumps(result['trace_content_manifest'],sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        result['status']='D_COMPLETE_NATIVE_GRAMMAR_BYTES_NONATOMIC_CANDIDATE_PENDING_E'
    except (ValueError,IndexError,AssertionError,TimeoutError,OSError) as e:
        result.update(status='HOLD_NO_COMPLETE_INPUT_CLEARANCE',error=repr(e))
        if last:result['first_rejected_record']=last.copy()
    finally:
        ns['instruction']=original
        result.update(wall_seconds=time.monotonic()-start,
          retained_zero_mask_extended_opcodes=dict(extra),new_native_executions=0,new_application_starts=0)
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    dest=OUT/'CANDIDATE_AUDIT.json'
    if dest.exists():raise ValueError('existing audit retained; do not repeat or overwrite')
    os.nice(10);os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
    # Git maps its existing packfile virtually; extract small immutable source
    # blobs before applying the strict parser-worker address-space cap. No
    # trace body is read before the cap, and no Git subprocess inherits it.
    ns,maps,sources=decoder()
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    resource.setrlimit(resource.RLIMIT_AS,(256*2**20,256*2**20))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*2**20,8*2**20))
    report={'authority_E_commit':E,'native_framework':NATIVE_FW,'scope':'D_OFFLINE_INPUT_SUITABILITY_NOT_NATIVE_EXECUTION_OR_E_ACCEPTANCE',
      'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_sha256':sources,
      'analysis_source_commit':source_commit,
      'analysis_driver_sha256':sha(Path(__file__).read_bytes()),'candidate_order':['spmv','scan','sgemm'],
      'order_reason':'original D preregistration: first fallback spmv; remaining existing inputs reviewed independently, no new speedup visible',
      'CPU_workers':1,'memory_cap_bytes':256*2**20,'per_candidate_seconds_cap':900,'batch_seconds_cap':1200,
      'no_original_five_or_dwt_trace_scans':True,'no_lease_or_E_ledger_mutation':True,'results':[]}
    candidates={r['workload']:r for r in json.loads((DOC/'INPUT_SELECTION.json').read_text())['candidates']}
    start=time.monotonic()
    for w in report['candidate_order']:
        if time.monotonic()-start>=1200:break
        r=audit(candidates[w],ns,maps,min(start+1200,time.monotonic()+900))
        report['results'].append(r);save(dest,report)
        print(json.dumps({'workload':w,'status':r['status'],'files_completed':len(r['files']),'error':r.get('error'),'seconds':r['wall_seconds']}),flush=True)
    report.update(finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
      peak_process_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
      new_compiler_or_simulator_starts=0,new_complete_app_starts=0,own_background_worker_after_exit=False)
    save(dest,report)

if __name__=='__main__':main()
