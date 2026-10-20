"""One-shot paper projection of E's accepted controls, not a second acceptor.

Call on each E incremental notice, with a NEW output revision. Reuses
full_v2_analysis.control_views and paper_four_pair_details' observation parser.
Never launches/polls/accepts, scans traces or modifies E's registry/manuscript.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import full_v2_analysis as full
import paper_four_pair_details as detail
import sync_intake as intake


def cached_observation(point,record,cache_dirs,out):
    """Reuse hash-bound snapshots; only a NEW accepted raw log is decoded."""
    expected=record['raw_log_sha256'];attempt=point['attempt_id']
    for directory in cache_dirs:
        manifest_path=directory/'FILES_SHA256.json'
        if not manifest_path.exists():continue
        manifest=json.loads(manifest_path.read_text())
        candidates=[(directory/('OBSERVATIONS_'+attempt+'.json'),None),
                    (directory/(point['workload']+'_SNAPSHOT_OBSERVATIONS.json'),point['profile'])]
        for path,label in candidates:
            if not path.exists() or manifest.get(path.name)!=intake.digest(path):continue
            obs=json.loads(path.read_text())
            if label:obs=obs.get(label)
            if obs and obs.get('sha256')==expected and Path(obs['path']).parent.name==attempt:
                return obs,dict(attempt_id=attempt,mode='HASH_BOUND_SNAPSHOT_REUSED',
                  cache_file=str(path),cache_file_sha256=intake.digest(path),raw_sha256=expected)
    path=Path('/workspace/ep_l2_ms20261019_e_results')/attempt/'raw.log'
    obs=detail.observe(path,expected)
    return obs,dict(attempt_id=attempt,mode='NEW_ACCEPTED_RAW_OBSERVED_ONCE',raw_path=str(path),raw_sha256=expected)


def timing_for_contrast(row,observations):
    left=observations[(row['workload'],row['left'])];right=observations[(row['workload'],row['right'])]
    if left['frames'][-1]['gpu_tot_sim_cycle']!=row['cycles_left'] or right['frames'][-1]['gpu_tot_sim_cycle']!=row['cycles_right']:
        raise ValueError('snapshot terminal clock differs from accepted endpoint')
    joined=detail.paired_timing(row['workload'],{'S':left,'F':right})
    for r in joined:
        r.update(left=row['left'],right=row['right'],left_attempt=row['left_attempt'],right_attempt=row['right_attempt'])
        r['right_minus_left_cycles']=r.pop('F_minus_S_cycles')
        for k in list(r):
            if k.startswith('S_'):r['left_'+k[2:]]=r.pop(k)
            elif k.startswith('F_'):r['right_'+k[2:]]=r.pop(k)
    if sum(r['right_minus_left_cycles'] for r in joined)!=row['cycles_right_minus_left']:
        raise ValueError('kernel + residual does not close to accepted whole program contrast')
    return joined


def render(result,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(10.5,3.4));fig.subplots_adjust(wspace=.38,bottom=.34,top=.83,left=.07,right=.98)
    pts={(p['workload'],p['profile']):p for p in result['points']}
    sets=[('convolutionSeparable',['S','W_ONLY','F_MINUS_V','F_MINUS_R','S_COPY_FREE','WV_T','WV_M','F']),
          ('dwt2d',['S','S_COPY_FREE','W_ONLY','F']),('cfd_097k',['S','F_MINUS_V','F_MINUS_R','F'])]
    for ax,(w,profiles) in zip(axes,sets):
        base=pts.get((w,'S'));ax.set_title({'convolutionSeparable':'Conv','dwt2d':'DWT','cfd_097k':'CFD'}[w],fontsize=11)
        for n,profile in enumerate(profiles):
            point=pts.get((w,profile))
            if base and point:
                value=100*(point['cycles']/base['cycles']-1)
                ax.bar(n,value,color='#416d86' if value<=0 else '#a65b50',width=.6)
                ax.annotate(f'{value:+.3f}',(n,value),xytext=(0,3 if value>=0 else -3),textcoords='offset points',ha='center',va='bottom' if value>=0 else 'top',fontsize=6,rotation=90)
            else:ax.text(n,0,'pending',rotation=90,va='bottom',ha='center',fontsize=7,color='#666666')
        ax.axhline(0,color='#777777',lw=.7);ax.set_xticks(range(len(profiles)),profiles,rotation=60,ha='right',fontsize=7)
        lo,hi=ax.get_ylim();span=max(hi-lo,1);ax.set_ylim(min(lo,-.2)-span*.35,max(hi,.2)+span*.35)
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Cycle change from same-input S (%)')
    fig.suptitle('Current E-accepted endpoints; each control updates independently',fontsize=12)
    fig.text(.5,.025,'Pending = no accepted measurement, never zero. COPY_FREE is a diagnostic counterfactual.\nConditional contrasts include state/queue interactions; request waits are not additive GPU stalls.',ha='center',fontsize=8)
    for ext in ['pdf','png']:fig.savefig(out/('INCREMENTAL_CONTROL_CONDITIONS.'+ext),dpi=200)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cache',type=Path,action='append',default=[]);parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):raise ValueError('use a new output revision; preserve old evidence')
    args.out.mkdir(parents=True,exist_ok=True)
    plan=json.loads(args.plan.read_text())
    with (intake.SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock,fcntl.LOCK_SH);raw=(intake.SHARED/'RUN_REGISTRY.json').read_bytes();ledger=json.loads(raw)[intake.FIELD]
    if ledger.get('owner')!='E' or ledger.get('campaign_id')!=full.CAMPAIGN or ledger.get('authority_commit') not in [full.AUTH,intake.AUTHORITY]:
        raise ValueError('wrong canonical E ledger')
    binding=full.accepted_display_binding(ledger,plan['source_identity']['binary_sha256'])
    holds=json.loads((full.OUT.parent/'input_suitability_20261020_r1/INPUT_APPLICABILITY.json').read_text())['holds']
    result=full.control_views(ledger,binding,plan,holds)
    full.csvout(args.out/'CONTROL_ACCEPTANCE_AND_ANCHORS.csv',result['controls'])
    full.csvout(args.out/'CONDITIONAL_COMPARISONS.csv',result['contrasts'])
    full.csvout(args.out/'CURRENT_ACCEPTED_PERFORMANCE.csv',full.performance_table(result['main']),
      ['workload','pair_id','cycles_left','cycles_right','ratio_left_over_right','speedup_percent'])
    full.csvout(args.out/'CURRENT_ENDPOINT_IDENTITIES.csv',[{k:v for k,v in p.items() if k!='mechanism_metrics'} for p in result['points']],
      ['workload','profile','attempt_id','receipt_sha256','cycles'])
    measurements=[]
    for row in result['main']['main']+result['details']:
        if row['status']=='E_ACCEPTED_D_ANALYZED':
            for m in full.mechanism_table(row):
                # Existing helper names its arbitrary endpoints S/F; relabel
                # those columns to prevent a control being called full F.
                m.update(left_profile=row.get('baseline_profile','S'),right_profile=row.get('variant_profile','F'))
                m['left']=m.pop('S');m['right']=m.pop('F');m['right_minus_left']=m.pop('F_minus_S');measurements.append(m)
    full.csvout(args.out/'RAW_MECHANISM_COUNTS.csv',measurements,
      ['pair_id','workload','left_profile','right_profile','metric','left','right','right_minus_left','scope'])
    observations={};provenance=[];timing=[];timing_holds=[]
    for point in result['points']:
        record=intake.pointer(ledger['accepted_results'][point['attempt_id']])
        try:
            obs,prov=cached_observation(point,record,args.cache,args.out)
            observations[(point['workload'],point['profile'])]=obs;provenance.append(prov)
            (args.out/('OBSERVATIONS_'+point['attempt_id']+'.json')).write_text(json.dumps(obs,indent=2)+'\n')
        except (ValueError,FileNotFoundError,KeyError) as e:
            timing_holds.append(dict(attempt_id=point['attempt_id'],reason=str(e)))
    for row in result['contrasts']:
        if row['status']!='CURRENT_D_DERIVED_CONTRAST':continue
        try:timing.extend(timing_for_contrast(row,observations))
        except (ValueError,KeyError) as e:timing_holds.append(dict(workload=row['workload'],left=row['left'],right=row['right'],reason=str(e)))
    full.csvout(args.out/'CONTROL_KERNEL_TIMING_AND_SNAPSHOTS.csv',timing,
      ['workload','left','right','kernel_ordinal','kernel_name','right_minus_left_cycles'])
    summary=dict(observed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),registry_sha256=hashlib.sha256(raw).hexdigest(),
      plan_sha256=intake.digest(args.plan),plan_E_commit=plan['E_commit'],
      accepted_controls=sum(r['status']=='E_ACCEPTED_D_ANALYZED' for r in result['controls']),planned_controls=len(plan['profiles']),
      current_main_summary=result['main']['summary'],RO_grid=result['RO_grid'],
      RO_cycle_interaction_C11_minus_C10_minus_C01_plus_C00=result['RO_cycle_interaction_C11_minus_C10_minus_C01_plus_C00'],
      snapshot_provenance=provenance,timing_holds=timing_holds,not_approved=plan['not_approved'],
      application_starts=0,trace_body_reads=0,acceptance_owner='E',new_acceptor=False,
      background_poller=False,manuscript_EN_v20_modified=False)
    (args.out/'INCREMENTAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.out/'CURRENT_E_PAIR_REFERENCES.json').write_text(json.dumps(ledger['accepted_pairs'],indent=2)+'\n')
    if args.render:
        full.render_accepted_performance(result['main'],args.out);render(result,args.out)
    manifest={p.name:intake.digest(p) for p in args.out.iterdir() if p.is_file()}
    (args.out/'FILES_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['accepted_controls','planned_controls','RO_grid','timing_holds']}))

if __name__=='__main__':main()
