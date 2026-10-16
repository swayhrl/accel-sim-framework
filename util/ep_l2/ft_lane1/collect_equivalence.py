#!/usr/bin/env python3
"""Compare only complete, content-identical-input old/new qualification rows."""
import argparse,csv,hashlib,json,re
from pathlib import Path

ARTIFACTS=['target_'+name+'.csv' for name in ('summary','slice','kernel','bank','l1','dram','window')]
OLD='4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617'
NEW='126394be46b15f55b9756d43eb9ca9a9baae1c84'
WORKLOADS=['vectorAdd_4M','cfd_097k','sad']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def metrics(path):
    result={}
    for line in path.open(errors='replace'):
        m=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if m:result[m[1]]=int(m[2])
    if result.keys()!={'cycle','insn'}:raise ValueError('native metrics absent')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    registry=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())
    chosen={}
    for key,row in registry['runs'].items():
        i=row['identity'];w=i['workload'];source=i['core_source_commit']
        if row['owner']!='lane1' or source not in (OLD,NEW) or w not in WORKLOADS:continue
        if row['status']!='COMPLETE_VALID':continue
        if (w,source) in chosen:raise ValueError('ambiguous source/workload control')
        root=Path(row['result_directory']);status=json.loads((root/'run_status.json').read_text())
        if status['status']!='COMPLETE_VALID' or sha(root/'raw.log')!=status['raw_log_sha256']:raise ValueError('control terminal/hash failed')
        if status['identity']!=i:raise ValueError('registry/runner identity mismatch')
        if sha(root/'accel-sim.out')!=i['binary_sha256']:raise ValueError('retained binary changed')
        chosen[w,source]=(key,root,i)
    missing=[(w,s) for w in WORKLOADS for s in (OLD,NEW) if (w,s) not in chosen]
    if missing:raise SystemExit('PENDING_CONTROLS '+json.dumps(missing))
    rows=[]
    for w in WORKLOADS:
        oldkey,old,oi=chosen[w,OLD];newkey,new,ni=chosen[w,NEW]
        for field in ['runtime_config_sha256','trace_content_sha256','feature_vector','ideal_vector','epoch_range']:
            if oi[field]!=ni[field]:raise ValueError('uncontrolled input delta '+w+' '+field)
        a,b=metrics(old/'raw.log'),metrics(new/'raw.log')
        equality=all(sha(old/f)==sha(new/f) for f in ARTIFACTS)
        if a!=b or not equality:raise ValueError('OLD_OFF_REGRESSION '+w)
        archive=Path('/workspace/results/ep_l2_m0a_m1_int/compact_gate_r1/BASE_M1_STATIC')/w
        if not all(sha(old/f)==sha(archive/f) for f in ARTIFACTS):raise ValueError('fresh old does not match history '+w)
        rows.append({'workload':w,'old_core':OLD,'new_core':NEW,'old_framework':oi['framework_source_commit'],'new_framework':ni['framework_source_commit'],
            'old_binary_sha256':oi['binary_sha256'],'new_binary_sha256':ni['binary_sha256'],'runtime_config_sha256':oi['runtime_config_sha256'],
            'trace_content_sha256':oi['trace_content_sha256'],'old_cycles':a['cycle'],'new_cycles':b['cycle'],'old_instructions':a['insn'],'new_instructions':b['insn'],
            'seven_csv_families':'BYTE_IDENTICAL','retained_history':'BYTE_IDENTICAL','old_run_key':oldkey,'new_run_key':newkey,'status':'PASS'})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    print('OLD_STATIC_EQUIVALENCE_PASS 3/3; cycles/instructions and 7 CSV families exact')

if __name__=='__main__':main()
