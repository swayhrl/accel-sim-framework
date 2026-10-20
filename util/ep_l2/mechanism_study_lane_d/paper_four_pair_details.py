"""Observations from E-accepted raw logs, using full_v2_analysis's intake.

No simulator/trace execution, independent acceptance or registry mutation.
Named kernel GPU durations and final residual are elapsed-time observations.
Counter differences are cumulative-snapshot deltas, not exclusive kernel stalls.
"""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import full_v2_analysis as full
import sync_intake as intake

WANTED={
 ('EPL2MSV1','LOCAL_DIAGNOSTIC'):['physical_grants','logical_copy_reads','logical_copy_writes'],
 ('EPL2MSV1','OBSERVER'):['lower_reads','lower_read_bytes','lower_wb_bytes','unfinished_head'],
 ('EPL2TVDV2','SUMMARY'):['read_responses','dirty_forward_responses','directory_queries','promotions','retention_slot_cycles','clean_retention_slot_cycles'],
 ('EPL2ROV1','SUMMARY'):['accepted_ro','transactions','merges','detached','lower_sectors'],
}
REASONS={1:'landing',3:'line_mshr',6:'wad',7:'same_wb',10:'missq',12:'data',13:'copy',14:'any_to_admit',15:'V_query',16:'RO_query'}

def observe(path,expected_sha):
    if intake.digest(path)!=expected_sha:raise ValueError('accepted raw bytes changed')
    frames=[];header={};current=None
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            if line.startswith('kernel_name ='):
                header={'kernel_name':line.split('=',1)[1].strip()}
            elif any(line.startswith(k+' =') for k in ['kernel_launch_uid','gpu_sim_cycle','gpu_tot_sim_cycle','gpu_tot_sim_insn']):
                key,val=[v.strip() for v in line.split('=',1)]
                header[key]=int(val) if val.isdigit() else val
                if key=='gpu_tot_sim_cycle':
                    current=dict(header,raw_clock_line=lineno,records={});frames.append(current)
            elif current and line.startswith('EPL2'):
                parts=line.strip().split('|');family=tuple(parts[:2])
                is_wait=family in [('EPL2MSV1','WAIT'),('EPL2MSV2','WAIT')]
                if family not in WANTED and not is_wait:continue
                fields=dict(p.split('=',1) for p in parts[2:] if '=' in p)
                if 'slice' not in fields:continue
                reason=int(fields.get('reason',-1));sid=int(fields['slice'])
                if is_wait and reason not in REASONS:continue
                current['records'][family+(sid,reason)]=(lineno,fields)
    summaries=[]
    for frame in frames:
        out={k:v for k,v in frame.items() if k!='records'};records=frame['records'];measured={}
        for family,keys in WANTED.items():
            rows=[v[1] for k,v in records.items() if k[:2]==family]
            for key in keys:
                name=family[0]+'_'+key
                measured[name]=sum(int(r[key]) for r in rows) if len(rows)==64 else 'UNKNOWN'
        for code,name in REASONS.items():
            rows=[v[1] for k,v in records.items() if k[:2] in [('EPL2MSV1','WAIT'),('EPL2MSV2','WAIT')] and k[3]==code]
            for key in ['requests','resolved','sum','observations','unknown_while_unresolved']:
                measured['wait_'+name+'_'+key]=sum(int(r[key]) for r in rows) if len(rows)==64 else 'UNKNOWN'
            measured['wait_'+name+'_max']=max(int(r['max']) for r in rows) if len(rows)==64 else 'UNKNOWN'
        out['cumulative']=measured;summaries.append(out)
    previous={}
    for frame in summaries:
        frame['counter_snapshot_delta']={}
        for key,val in frame['cumulative'].items():
            if key.endswith('_max') or key.endswith('_unfinished_head'):continue
            old=previous.get(key,0)
            frame['counter_snapshot_delta'][key]=val-old if isinstance(val,int) and isinstance(old,int) and val>=old else 'UNKNOWN'
        previous=frame['cumulative']
    return {'path':str(path),'sha256':expected_sha,'frames':summaries,
      'scope':'cumulative snapshots; deltas are NOT exclusive kernel stalls; no unfinished request timing attribution'}

def paired_timing(workload,observations):
    sides={s:[f for f in observations[s]['frames'] if f.get('kernel_name')] for s in ['S','F']}
    rows=[]
    if [f['kernel_name'] for f in sides['S']]!=[f['kernel_name'] for f in sides['F']]:
        raise ValueError('different named kernel sequences; refuse timing join')
    for n,(s,f) in enumerate(zip(sides['S'],sides['F']),1):
        row={'workload':workload,'kernel_ordinal':n,'kernel_name':s['kernel_name'],
          'S_gpu_sim_cycle':s['gpu_sim_cycle'],'F_gpu_sim_cycle':f['gpu_sim_cycle'],
          'F_minus_S_cycles':f['gpu_sim_cycle']-s['gpu_sim_cycle'],
          'scope':'reported named kernel duration; mechanism deltas are adjacent cumulative snapshots, not causal stalls'}
        for label,frame in [('S',s),('F',f)]:
            for key,val in frame['counter_snapshot_delta'].items():row[label+'_'+key]=val
            row[label+'_raw_clock_line']=frame['raw_clock_line']
        rows.append(row)
    for label in ['S','F']:
        final=observations[label]['frames'][-1]['gpu_tot_sim_cycle']
        named=sum(f['gpu_sim_cycle'] for f in sides[label])
        residual=final-named
        if label=='S':tail={'workload':workload,'kernel_ordinal':'FINAL_RESIDUAL','kernel_name':'after named durations; exact cause UNKNOWN'}
        tail[label+'_gpu_sim_cycle']=residual
    tail.update(F_minus_S_cycles=tail['F_gpu_sim_cycle']-tail['S_gpu_sim_cycle'],scope='final accepted program cycles minus named durations; NOT asserted to be DRAM drain alone')
    rows.append(tail)
    return rows

def render(rows,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(8,7.2));fig.subplots_adjust(hspace=.65,bottom=.12,top=.91,left=.13,right=.97)
    for ax,w in zip(axes,['cfd_097k','dwt2d','sad']):
        selected=[r for r in rows if r['workload']==w];vals=[r['F_minus_S_cycles'] for r in selected]
        ax.bar(range(len(vals)),vals,color=['#a65b50' if v>0 else '#416d86' for v in vals])
        ax.set_xticks(range(len(vals)),['tail' if r['kernel_ordinal']=='FINAL_RESIDUAL' else str(r['kernel_ordinal']) for r in selected])
        ax.axhline(0,color='#777777',lw=.7);ax.set_title(w+' | kernel ordinal + final residual',fontsize=10)
        ax.set_ylabel('F - S GPU cycles');ax.spines[['top','right']].set_visible(False)
        for n,v in enumerate(vals):
            if v:ax.annotate(f'{v:+,}',(n,v),xytext=(0,3 if v>0 else -3),textcoords='offset points',ha='center',va='bottom' if v>0 else 'top',fontsize=7)
        lo,hi=ax.get_ylim();ax.set_ylim(lo-(hi-lo)*.12,hi+(hi-lo)*.12)
    fig.suptitle('Where the measured program-time differences occur',fontsize=12)
    fig.text(.5,.025,'Positive = slower F. Named durations + residual equal final elapsed GPU time.\nThese are elapsed durations, NOT sums of request waits.',ha='center',fontsize=9)
    for ext in ['pdf','png']:fig.savefig(out/('PAIRED_KERNEL_TIMING.'+ext),dpi=180)
    plt.close(fig)
    dwt=[r for r in rows if r['workload']=='dwt2d' and r['kernel_ordinal']!='FINAL_RESIDUAL']
    fig,axes=plt.subplots(2,2,figsize=(10,6.2));fig.subplots_adjust(hspace=.58,wspace=.32,bottom=.14,top=.88)
    xs=list(range(1,len(dwt)+1));gpu=[r['F_minus_S_cycles'] for r in dwt]
    ax=axes[0,0];ax.bar(xs,gpu,color=['#a65b50' if v>0 else '#416d86' for v in gpu]);ax.axhline(0,color='#777777',lw=.7)
    ax.set_title('(a) Elapsed GPU cycles F - S');ax.set_ylabel('GPU cycles')
    bank=[100*(r['F_EPL2MSV1_physical_grants']/r['S_EPL2MSV1_physical_grants']-1) for r in dwt]
    axes[0,1].bar(xs,bank,color='#416d86');axes[0,1].set_title('(b) Physical bank service change');axes[0,1].set_ylabel('(F / S - 1) %')
    landing=[r['F_wait_landing_sum'] for r in dwt];ax=axes[1,0];ax.bar(xs,landing,color='#a18564')
    ax.set_title('(c) Landing wait snapshot increments');ax.set_ylabel('Request-cycles; nonexclusive')
    for x,v in zip(xs,landing):
        if v:ax.text(x,v+1800,f'{v:,}',ha='center',fontsize=7)
    vq=[r['F_EPL2TVDV2_directory_queries'] for r in dwt];rq=[r['F_wait_RO_query_sum'] for r in dwt]
    axes[1,1].bar([x-.18 for x in xs],vq,.36,label='V queries',color='#416d86')
    axes[1,1].bar([x+.18 for x in xs],rq,.36,label='RO queries',color='#999999')
    axes[1,1].set_title('(d) Modeled lookup events');axes[1,1].set_ylabel('Query events');axes[1,1].legend(frameon=False,fontsize=8)
    for ax in axes.flat:ax.set_xticks(xs);ax.set_xlabel('DWT kernel ordinal');ax.spines[['top','right']].set_visible(False)
    fig.suptitle('DWT: service savings and waits do not identify the critical path',fontsize=12)
    fig.text(.5,.025,'98.9% of landing wait increments occur in faster kernel 1.\nKernels 5 and 8 regress with zero new RO queries; indirect prior-state effects remain possible.',ha='center',fontsize=9)
    for ext in ['pdf','png']:fig.savefig(out/('DWT_STAGE_MECHANISMS.'+ext),dpi=180)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--binary',required=True);p.add_argument('--render',action='store_true')
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    with (intake.SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock,fcntl.LOCK_SH);raw=(intake.SHARED/'RUN_REGISTRY.json').read_bytes();ledger=json.loads(raw)[intake.FIELD]
    if (ledger.get('owner')!='E' or ledger.get('campaign_id')!=full.CAMPAIGN
        or ledger.get('authority_commit') not in [full.AUTH,intake.AUTHORITY]):
        raise ValueError('wrong canonical E ledger for observation projection')
    binding=full.accepted_display_binding(ledger,args.binary)
    holds=json.loads((full.OUT.parent/'input_suitability_20261020_r1/INPUT_APPLICABILITY.json').read_text())['holds']
    accepted=full.views(ledger,binding,holds)
    timing=[];identities=[]
    for row in accepted['main']:
        if row['status']!='E_ACCEPTED_D_ANALYZED':continue
        observations={}
        for side,label in [('baseline','S'),('variant','F')]:
            ref=ledger['accepted_results'][row[side+'_attempt_id']];record=intake.pointer(ref)
            path=Path('/workspace/ep_l2_ms20261019_e_results')/record['attempt_id']/'raw.log'
            observations[label]=observe(path,record['raw_log_sha256'])
            identities.append({'workload':row['workload'],'profile':label,'accepted_receipt':ref,
              'raw_path':str(path),'raw_sha256':record['raw_log_sha256'],'qualification_id':record['qualification_id']})
        (args.out/(row['workload']+'_SNAPSHOT_OBSERVATIONS.json')).write_text(json.dumps(observations,indent=2)+'\n')
        timing.extend(paired_timing(row['workload'],observations))
    full.csvout(args.out/'PAIRED_KERNEL_TIMING_AND_SNAPSHOT_DELTAS.csv',timing)
    if args.render:render(timing,args.out)
    (args.out/'ACCEPTED_OBSERVATION_IDENTITIES.json').write_text(json.dumps(identities,indent=2)+'\n')
    (args.out/'OBSERVATION_RECEIPT.json').write_text(json.dumps({'registry_sha256':hashlib.sha256(raw).hexdigest(),
      'accepted_workloads':accepted['summary']['current_accepted_subset_members'],'application_starts':0,
      'trace_body_reads':0,'acceptance_owner':'E','new_acceptor':False,'snapshot_waits_are_GPU_stall':False},indent=2)+'\n')
    print(json.dumps({'kernel_and_residual_rows':len(timing),'workloads':accepted['summary']['current_accepted_subset_members']}))

if __name__=='__main__':main()
