"""One-shot V2 display/analysis of E-accepted pairs; never accepts or runs apps.

The small E_VIEW_BINDINGS artifact maps E's existing pair IDs and qualified
profile names to D's planned conditions. It is a display mapping, not another
qualification system, queue or scheduler. Until E publishes it all cells stay
unmeasured. A seven-workload mean is emitted only for the full common release.
"""
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
from pathlib import Path
import sync_intake as intake
from prepare_full_v2 import AUTH, CAMPAIGN, WORKLOADS, REPS, matrix

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/full_system_v2'
UNKNOWN='UNKNOWN'

def comparisons():
    rows=[]
    def add(w,left,right,kind):
        rows.append({'comparison_id':f'{w}__{left}__{right}','workload':w,'kind':kind,
          'left':f'V2_{w}_{left}','right':f'V2_{w}_{right}',
          'ratio_definition':'cycles(left)/cycles(right); >1 right faster; <1 right slower'})
    for w in WORKLOADS:add(w,'S','F','MAIN')
    for w in REPS:
        for p in ['F_MINUS_W','F_MINUS_V','F_MINUS_R']:add(w,p,'F','REMOVE_ONE')
        add(w,'S','W_ONLY','W_ONLY');add(w,'W_ONLY','F','BEYOND_W')
    for p in ['WV_T','WV_M']:add(REPS[0],'F_MINUS_R',p,'RO_FACTORIAL')
    add(REPS[0],'F_FIXED_V64','F','FIXED_VICTIM')
    for w in REPS:
        for left,right in [('S','S_COPY_FREE'),('S','S_L2_DATA_FREE'),('F','F_L2_DATA_FREE')]:
            add(w,left,right,'LOCAL_DIAGNOSTIC')
    add(REPS[0],'S','S_WB64','STATIC_CAPACITY')
    return rows

def qualification(ledger,binding):
    """Use E's current qualification pointer; do not rerun/reinterpret its gates."""
    qid=binding.get('qualification_id')
    ref=ledger.get('qualifications',{}).get(qid)
    if not ref:raise ValueError('final E qualification missing')
    q=intake.pointer(ref)
    if ref.get('qualification')!=q:raise ValueError('qualification bytes/projection changed')
    if q.get('qualified_by')!='E' or q.get('status')!='INDEPENDENTLY_QUALIFIED':
        raise ValueError('not independently E qualified')
    if q.get('campaign_id')!=CAMPAIGN:raise ValueError('wrong qualification campaign')
    if q.get('source_identity')!=binding.get('source_identity'):raise ValueError('final source binding differs')
    hold=ledger.get('scientific_holds',{}).get(qid)
    if hold and hold.get('status') not in ['RESOLVED','CLEARED']:
        raise ValueError('current final qualification scientific hold')
    if not binding.get('fixed_policy_sha256') or len(binding['fixed_policy_sha256'])!=64:
        raise ValueError('final fixed policy unbound')
    if binding.get('full_victim_semantics')!='CLEAN_DIRTY_PENDING_INFLIGHT':
        raise ValueError('clean-only is not the full scheme')
    return q

def views(ledger,binding):
    planned={r['condition_id']:r for r in matrix()}
    endpoints={};results=[];problem=None
    if binding:
        try:q=qualification(ledger,binding)
        except (ValueError,KeyError,FileNotFoundError,TypeError) as e:problem=str(e)
    else:problem='UNASSIGNED_FINAL_A_RELEASE_AND_E_DISPLAY_BINDING'
    for cmp in comparisons():
        row=dict(cmp,status='UNMEASURED',cycles_left=UNKNOWN,cycles_right=UNKNOWN,
          ratio_left_over_right=UNKNOWN,cycles_left_minus_right=UNKNOWN,pair_id=UNKNOWN,
          binary=UNKNOWN,bottleneck=UNKNOWN,trigger=UNKNOWN,local_service=UNKNOWN,
          mechanism_causality='UNKNOWN_REQUIRES_RUNTIME_FOUR_LAYER_CHAIN')
        mapping=(binding or {}).get('pairs',{}).get(cmp['comparison_id'])
        if problem:row['reason']=problem
        elif not mapping:row['reason']='NO_E_ACCEPTED_PAIR_BINDING'
        else:
            try:
                pid=mapping['pair_id'];decl=ledger['accepted_pairs'][pid]
                parsed=intake.analyze_pair(pid,decl,ledger['accepted_results'])
                if parsed['status']!='E_ACCEPTED_D_ANALYZED':raise ValueError(parsed['status'])
                src=binding['source_identity']
                for key,field in [('core','core_source_commit'),('framework','framework_source_commit'),
                                  ('vendor','vendor_pybind11_commit'),('binary','binary_sha256')]:
                    if parsed[key]!=src[field]:raise ValueError('pair outside final common source: '+key)
                if parsed['workload']!=cmp['workload']:raise ValueError('wrong workload')
                if any(parsed[side+'_qualification_id']!=binding['qualification_id'] for side in ['baseline','variant']):
                    raise ValueError('endpoint not bound to current final E qualification')
                if mapping['left']!=cmp['left'] or mapping['right']!=cmp['right']:
                    raise ValueError('reversed/incorrect display condition mapping')
                pending={}
                for side,condition in [('baseline',cmp['left']),('variant',cmp['right'])]:
                    expected=binding['condition_profiles'][condition]
                    if expected not in q['supported_profiles'] or parsed[side+'_profile']!=expected:
                        raise ValueError('condition/profile is not E qualified')
                    # Conditions remain unsupported until explicitly in E's accepted profile table.
                    point={k:parsed[side+'_'+k] for k in ['cycles','instructions','config','receipt_sha256','attempt_id']}
                    point.update(trace=parsed['trace'],binary=parsed['binary'])
                    if condition in endpoints and point!=endpoints[condition]:
                        raise ValueError('same condition silently mapped to another accepted endpoint')
                    pending[condition]=point
                endpoints.update(pending)
                row.update(status='E_ACCEPTED_D_ANALYZED',reason='CURRENT_E_PAIR_EXACT_FINAL_RELEASE',
                  pair_id=pid,cycles_left=parsed['baseline_cycles'],cycles_right=parsed['variant_cycles'],
                  ratio_left_over_right=parsed['baseline_over_variant'],
                  cycles_left_minus_right=parsed['cycles_baseline_minus_variant'],binary=parsed['binary'],
                  bottleneck=parsed['bottleneck'],trigger=parsed['trigger'],local_service=parsed['local_service'],
                  baseline_mechanism_metrics=parsed['baseline_mechanism_metrics'],
                  variant_mechanism_metrics=parsed['variant_mechanism_metrics'])
            except (ValueError,KeyError,FileNotFoundError,TypeError) as e:row.update(status='D_DISPLAY_BINDING_HOLD',reason=str(e))
        results.append(row)
    main=[r for r in results if r['kind']=='MAIN']
    accepted=[r for r in main if r['status']=='E_ACCEPTED_D_ANALYZED']
    # Never a partial-best or cross-source seven-input mean.
    mean=math.exp(sum(math.log(r['ratio_left_over_right']) for r in accepted)/7) if len(accepted)==7 else UNKNOWN
    coverage=[]
    for w in WORKLOADS:
        r=next(r for r in main if r['workload']==w)
        for p,side in [('S','left'),('F','right')]:
            coverage.append({'workload':w,'condition_id':f'V2_{w}_{p}','scheme':p,
              'status':r['status'],'cycles':r['cycles_'+side],
              'ratio_S_over_F':r['ratio_left_over_right'] if p=='F' else UNKNOWN,
              'binary':r['binary'],'pair_id':r['pair_id'],'reason':r.get('reason',UNKNOWN)})
    grid={p:endpoints.get('V2_'+REPS[0]+'_'+p) for p in ['F_MINUS_R','WV_T','WV_M','F']}
    interaction=UNKNOWN
    if all(grid.values()):
        interaction=int(grid['F']['cycles'])-int(grid['WV_T']['cycles'])-int(grid['WV_M']['cycles'])+int(grid['F_MINUS_R']['cycles'])
    return {'main':main,'comparisons':results,'coverage':coverage,
      'summary':{'seven_input_geomean_S_over_F':mean,'current_accepted_main_pairs':len(accepted),
        'required_main_pairs':7,'actual_starts_from_E':ledger.get('actual_starts'),
        'authorized_cumulative_max':40,'counter_reset':False,'analysis_is_not_qualification':True,
        'final_binary':(binding or {}).get('source_identity',{}).get('binary_sha256',UNKNOWN),
        'RO_grid':grid,'RO_cycle_interaction_C11_minus_C10_minus_C01_plus_C00':interaction,
        'RO_interpretation':'signed cycle interaction at same WV background; not an exclusive stall-time decomposition',
        'no_background_poller':True,'paper_EN_v17_modified':False}}

def csvout(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n')
        w.writeheader();w.writerows(rows)

def render(result,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    font=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
    fig,ax=plt.subplots(figsize=(8.1,3.4))
    fig.subplots_adjust(left=.10,right=.98,bottom=.24,top=.85)
    labels=['SAD','向量加法','CFD','可分离卷积','快速Walsh','B树','二维小波']
    vals=[float(r['ratio_left_over_right']) if r['status']=='E_ACCEPTED_D_ANALYZED' else float('nan') for r in result['main']]
    valid=[x for x in vals if math.isfinite(x)]
    upper=max([1.2]+[x*1.15 for x in valid]);ax.set_ylim(0,upper);ax.set_xlim(-.65,6.65)
    for x,v in enumerate(vals):
        if math.isfinite(v):
            ax.bar(x,v,width=.58,color='#416d86');ax.text(x,v+.025,f'{v:.4f}',ha='center',fontsize=8)
        else:ax.text(x,.48*upper,'待E接受',ha='center',fontproperties=font,fontsize=9,color='#777777')
    ax.axhline(1,color='#777777',ls='--',lw=.8)
    ax.set_xticks(range(7),labels,fontproperties=font,fontsize=9)
    ax.set_ylabel('传统周期 / 完整方案周期',fontproperties=font)
    ax.set_title('七应用共同主比较：同一最终binary、固定完整策略',fontproperties=font,fontsize=11)
    ax.spines[['top','right']].set_visible(False)
    mean=result['summary']['seven_input_geomean_S_over_F']
    note='完整7对几何均值：待测' if mean==UNKNOWN else f'完整7对几何均值：{mean:.5f}'
    fig.text(.5,.045,note+'；虚线为参考1，不代表未测基线值。',ha='center',fontproperties=font,fontsize=8)
    for ext in ['pdf','png']:fig.savefig(out/('MAIN_SEVEN_S_F.'+ext),dpi=180)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--render',action='store_true');p.add_argument('--out',type=Path,default=OUT)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with (intake.SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock,fcntl.LOCK_SH)
        raw=(intake.SHARED/'RUN_REGISTRY.json').read_bytes();ledger=json.loads(raw)[intake.FIELD]
    if ledger.get('owner')!='E' or ledger.get('campaign_id')!=CAMPAIGN or ledger.get('authority_commit') not in [AUTH,intake.AUTHORITY]:
        raise ValueError('wrong canonical E ledger')
    # E may publish this optional, hash-bound display map with an event. No D
    # hand-written launch/qualification path exists, and no fallback matches by cycles.
    binding_ref=ledger.get('full_system_v2_analysis_bindings')
    binding=intake.pointer(binding_ref) if binding_ref else None
    if binding and (binding.get('owner')!='E' or binding.get('authority')!=AUTH):
        raise ValueError('unreviewed/wrong-authority display map')
    result=views(ledger,binding)
    for name,key in [('MAIN_COVERAGE_14.csv','coverage'),('COMPARISONS_AND_INTERPRETATION.csv','comparisons')]:csvout(a.out/name,result[key])
    result['summary'].update(registry_sha256_at_read=hashlib.sha256(raw).hexdigest(),
      observed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),authority=AUTH)
    (a.out/'ANALYSIS_SUMMARY.json').write_text(json.dumps(result['summary'],ensure_ascii=False,indent=2)+'\n')
    state_path=a.out/'ANALYSIS_HISTORY.json';history=json.loads(state_path.read_text()) if state_path.exists() else []
    fingerprint=hashlib.sha256(intake.canonical(result['comparisons'])).hexdigest()
    if not history or history[-1]['fingerprint']!=fingerprint:
        history.append({'fingerprint':fingerprint,'at_utc':result['summary']['observed_utc'],'comparisons':result['comparisons']})
        state_path.write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
    if a.render:render(result,a.out)
    print(json.dumps({k:v for k,v in result['summary'].items() if k!='RO_grid'}))

if __name__=='__main__':main()
