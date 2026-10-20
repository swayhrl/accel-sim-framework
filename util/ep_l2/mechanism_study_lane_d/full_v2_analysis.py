"""One-shot V2 display/analysis of E-accepted pairs; never accepts or runs apps.

E's accepted pair identities/profiles map directly to planned conditions when
no optional display binding exists. This is a projection of E's decisions,
never another acceptor. A seven-workload mean needs one common binary.
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

def qualification(ledger,binding,qid=None):
    """Use E's current qualification pointer; do not rerun/reinterpret its gates."""
    qid=qid or binding.get('qualification_id')
    ref=ledger.get('qualifications',{}).get(qid)
    if not ref:raise ValueError('final E qualification missing')
    q=intake.pointer(ref)
    if ref.get('qualification')!=q:raise ValueError('qualification bytes/projection changed')
    if q.get('qualified_by')!='E' or q.get('status')!='INDEPENDENTLY_QUALIFIED':
        raise ValueError('not independently E qualified')
    if q.get('campaign_id')!=CAMPAIGN:raise ValueError('wrong qualification campaign')
    if q.get('source_identity')!=binding.get('source_identity'):raise ValueError('final source binding differs')
    for key in [qid,'qualification:'+qid]:
        hold=ledger.get('scientific_holds',{}).get(key)
        if hold and hold.get('status') not in ['RESOLVED','CLEARED']:
            raise ValueError('current final qualification scientific hold')
    if binding.get('derived_from_E_accepted_pairs'):
        v2=q.get('full_system_v2',{})
        if (v2.get('authority_commit')!=AUTH or v2.get('fixed_policy') is not True
            or v2.get('victim_scope')!='CLEAN_DIRTY_PENDING_INFLIGHT'):
            raise ValueError('E qualification lacks fixed full V2 scope')
        return q
    if not binding.get('fixed_policy_sha256') or len(binding['fixed_policy_sha256'])!=64:
        raise ValueError('final fixed policy unbound')
    if binding.get('full_victim_semantics')!='CLEAN_DIRTY_PENDING_INFLIGHT':
        raise ValueError('clean-only is not the full scheme')
    return q

def accepted_display_binding(ledger,binary=None):
    """Map explicit E endpoint profile names, never guess from cycles.

    Different qualified parser revisions may bind S and F on the SAME runtime.
    Each current endpoint retains its own exact qualification pointer. Ambiguous
    sources/pairs are refused rather than choosing a favorable result.
    """
    candidates=[]
    for pid,decl in ledger.get('accepted_pairs',{}).items():
        pair=intake.pointer(decl) if 'path' in decl else decl
        if pair.get('status') not in ['CURRENT_ACCEPTED','ACCEPTED','COMPLETE_VALID']:continue
        try:
            parsed=intake.analyze_pair(pid,decl,ledger.get('accepted_results',{}))
            if parsed['status']!='E_ACCEPTED_D_ANALYZED':continue
            if binary and parsed['binary']!=binary:continue
            candidates.append(parsed)
        except (ValueError,KeyError,FileNotFoundError,TypeError):continue
    sources={(p['core'],p['framework'],p['vendor'],p['binary']) for p in candidates}
    if len(sources)!=1:return None
    core,fw,vendor,sha=next(iter(sources))
    binding={'owner':'E','authority':AUTH,'derived_from_E_accepted_pairs':True,
      'source_identity':dict(core_source_commit=core,framework_source_commit=fw,
                            vendor_pybind11_commit=vendor,binary_sha256=sha),
      'condition_profiles':{r['condition_id']:r['profile'] for r in matrix()},
      'pairs':{}}
    for p in candidates:
        for cmp in comparisons():
            if (p['workload']==cmp['workload'] and
                p['baseline_profile']==binding['condition_profiles'][cmp['left']] and
                p['variant_profile']==binding['condition_profiles'][cmp['right']]):
                key=cmp['comparison_id']
                if key in binding['pairs']:raise ValueError('ambiguous E pairs for condition: '+key)
                binding['pairs'][key]={'pair_id':p['pair_id'],'left':cmp['left'],'right':cmp['right'],
                  'endpoint_qualification_ids':{side:p[side+'_qualification_id'] for side in ['baseline','variant']}}
    return binding

def views(ledger,binding,input_holds=None):
    planned={r['condition_id']:r for r in matrix()}
    endpoints={};results=[];problem=None
    if binding and not binding.get('derived_from_E_accepted_pairs'):
        try:q=qualification(ledger,binding)
        except (ValueError,KeyError,FileNotFoundError,TypeError) as e:problem=str(e)
    elif not binding:problem='UNASSIGNED_FINAL_A_RELEASE_AND_E_DISPLAY_BINDING'
    for cmp in comparisons():
        row=dict(cmp,status='UNMEASURED',cycles_left=UNKNOWN,cycles_right=UNKNOWN,
          ratio_left_over_right=UNKNOWN,cycles_left_minus_right=UNKNOWN,pair_id=UNKNOWN,
          binary=UNKNOWN,bottleneck=UNKNOWN,trigger=UNKNOWN,local_service=UNKNOWN,
          mechanism_causality='UNKNOWN_REQUIRES_RUNTIME_FOUR_LAYER_CHAIN')
        mapping=(binding or {}).get('pairs',{}).get(cmp['comparison_id'])
        hold=(input_holds or {}).get(cmp['workload'])
        if hold and hold.get('status')=='HOLD':
            row.update(status='HOLD_INPUT_SCIENTIFIC_SCOPE',reason=hold['reason'])
        elif problem:row['reason']=problem
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
                qualified={}
                for side in ['baseline','variant']:
                    qid=mapping.get('endpoint_qualification_ids',{}).get(side,binding.get('qualification_id'))
                    if parsed[side+'_qualification_id']!=qid:
                        raise ValueError('endpoint not bound to current final E qualification')
                    qualified[side]=qualification(ledger,binding,qid)
                if mapping['left']!=cmp['left'] or mapping['right']!=cmp['right']:
                    raise ValueError('reversed/incorrect display condition mapping')
                pending={}
                for side,condition in [('baseline',cmp['left']),('variant',cmp['right'])]:
                    expected=binding['condition_profiles'][condition]
                    if expected not in qualified[side]['supported_profiles'] or parsed[side+'_profile']!=expected:
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
                for side in ['baseline','variant']:
                    for field in ['attempt_id','run_key','config','qualification_id','receipt_sha256','instructions']:
                        row[side+'_'+field]=parsed[side+'_'+field]
                row.update(core=parsed['core'],framework=parsed['framework'],vendor=parsed['vendor'],trace=parsed['trace'])
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
        'no_background_poller':True,'paper_EN_v17_modified':False,'paper_EN_v20_modified':False}}

def csvout(path,rows,empty_fields=None):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)) or empty_fields or [],lineterminator='\n')
        w.writeheader();w.writerows(rows)

def mechanism_table(row):
    """Observational projection of E's final counters, not another acceptor.

    Sum only named additive counters across final64 slices. Peak, latency,
    capacity, flag and timestamp fields are NEVER summed. OFF/missing is UNKNOWN.
    Request waits remain nonexclusive and are not a program-time decomposition.
    """
    metrics=[json.loads(row[s+'_mechanism_metrics']) if row.get(s+'_mechanism_metrics') not in [None,UNKNOWN] else {}
             for s in ['baseline','variant']]
    flat=[]
    def add(family,key,values,unit,scope):
        left,right=values
        flat.append(dict(pair_id=row['pair_id'],workload=row['workload'],family=family,
          metric=key,unit=unit,scope=scope,evidence_class='MEASURED_E_ACCEPTED_TERMINAL',
          S=left,F=right,F_minus_S=right-left if all(isinstance(x,(int,float)) for x in values) else UNKNOWN))
    def pathval(obj,path):
        for k in path:
            if not isinstance(obj,dict) or k not in obj:return UNKNOWN
            obj=obj[k]
        return obj
    for group,keys,unit in [
      ('trigger',['logical_copy_reads','logical_copy_writes'],'operations'),
      ('local_service',['physical_bank_grants','lower_reads'],'operations'),
      ('local_service',['lower_read_bytes','lower_wb_bytes'],'bytes')]:
        for k in keys:add(group,k,[pathval(m,[group,k]) for m in metrics],unit,'whole application; final cumulative64-slice sum')
    for reason in sorted(set().union(*(m.get('bottleneck',{}) if isinstance(m.get('bottleneck'),dict) else {} for m in metrics))):
        for k in ['distinct_requests_first_block','request_wait_cycle_sum','request_wait_max','blocked_observations_over_slices']:
            add('wait_'+reason,k,[pathval(m,['bottleneck',reason,k]) for m in metrics],
              'request-cycles_NONEXCLUSIVE' if k=='request_wait_cycle_sum' else 'requests' if k=='distinct_requests_first_block' else 'cycles_max' if k=='request_wait_max' else 'slice-observations',
              'per reason; requests/slices/reasons overlap; NEVER sum into GPU stall')
    def sums(family,group,keys,unit,scope):
        for k in keys:
            vals=[]
            for m in metrics:
                records=m.get('full_mechanism_records',{}).get(family,{})
                rows=[r.get(group,{}) if group else r for r in records.values()]
                vals.append(sum(r[k] for r in rows) if len(rows)==64 and all(isinstance(r.get(k),(int,float)) for r in rows) else UNKNOWN)
            add(family+('_'+group if group else ''),k,vals,unit,scope)
    sums('victim',None,['clean_installs','dirty_installs','read_responses','dirty_forward_responses',
      'served_sectors','promotions','directory_queries'],'events','final cumulative64-slice sum; OFF has no native records')
    sums('victim',None,['served_sector_bytes'],'bytes','served32B sectors')
    sums('victim',None,['clean_retention_slot_cycles','retention_slot_cycles','total_retention_slot_cycles'],
      'slot-cycles','occupancy integral; dirty field includes WB_INFLIGHT and WB_COMPLETE, excludes WB_STAGED')
    sums('victim',None,['lookup_wait_cycles','wb_wait_cycles','bank_wait_cycles','icnt_wait_cycles'],
      'wait-observations_NONEXCLUSIVE','internal counters overlap frontend wait reasons; do not add again')
    sums('readonly','summary',['accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions',
      'merges','detached','lower_sectors','concurrent_duplicate_sectors','responses','ro_bank_fill_ops','ro_bank_response_ops'],
      'events','accepted reads/candidates/admissions are nested; duplicates only concurrent same-sector lower')
    sums('readonly','resource',['normal_line_allocations','avoided_line_allocations','query_count','query_port_wait_attempts'],
      'events','line allocations avoided != blocked requests avoided; no cross-module counter addition')
    sums('readonly','resource',['lower_read_bytes','concurrent_duplicate_read_bytes'],
      'bytes','RO subset already contained in all lower traffic')
    sums('readonly','resource',['query_wait_cycles'],'wait-observations_NONEXCLUSIVE','same RO lookup events as frontend reason; do not double count')
    for group,keys in [('resource',['peak_transactions','peak_shared_descriptors','peak_shared_lines']),
                       ('lower_concurrency',['peak_independent_lower_lines','peak_lower_transactions'])]:
        for k in keys:
            for op in ['min','max']:
                vals=[]
                for m in metrics:
                    rows=m.get('full_mechanism_records',{}).get('readonly',{})
                    v=[r[group][k] for r in rows.values() if k in r.get(group,{})]
                    vals.append((min(v) if op=='min' else max(v)) if len(v)==64 else UNKNOWN)
                add('readonly_'+group,k+'_'+op+'_across_slices',vals,'per-slice highwater',
                  'range of individual slice peaks; simultaneous global peak UNKNOWN')
    return flat

def terminal_cost_observations(ledger,row,result_root):
    """Read extra cost counters from E-accepted raw bytes, never qualify them.

    E's decoder validates metadata costs but omits their projection. Retain
    only the LAST record per slice/bank; earlier cumulative snapshots must
    not be added. A raw-byte hash mismatch refuses this optional observation.
    """
    samples={};provenance={}
    for side in ['baseline','variant']:
        ref=ledger['accepted_results'][row[side+'_attempt_id']]
        receipt=intake.pointer(ref)
        path=result_root/receipt['attempt_id']/'raw.log'
        if intake.digest(path)!=receipt['raw_log_sha256']:raise ValueError('changed accepted raw for cost observation')
        last={}
        with path.open() as stream:
            for lineno,line in enumerate(stream,1):
                if line.startswith(('EPL2TVDV3|METADATA_COST|','EPL2SERVICEV1|RG1_BANK|')):
                    fields=dict(p.split('=',1) for p in line.strip().split('|')[2:])
                    key=(line.split('|')[1],int(fields['slice']),int(fields.get('bank',-1)))
                    last[key]={'raw_line':lineno,'fields':fields}
        samples[side]=last
        provenance[side]={'path':str(path),'sha256':receipt['raw_log_sha256'],
          'method':'last matching cumulative record per slice/bank, not sum over kernel snapshots',
          'records':[dict(record_kind=k[0],slice=k[1],bank=k[2],**v) for k,v in sorted(last.items())]}
    rows=[]
    for k in ['frontend_cam_queries','completion_cam_queries','indexed_wb_accept','indexed_rollback',
              'native_install_commits','native_promotion_commits']:
        vals=[]
        for side in ['baseline','variant']:
            records=[v['fields'] for key,v in samples[side].items() if key[0]=='METADATA_COST']
            vals.append(sum(int(r[k]) for r in records) if len(records)==64 else UNKNOWN)
        rows.append(dict(pair_id=row['pair_id'],workload=row['workload'],family='victim_metadata_cost',
          metric=k,S=vals[0],F=vals[1],F_minus_S=vals[1]-vals[0] if all(isinstance(x,int) for x in vals) else UNKNOWN,
          unit='events',evidence_class='OBSERVATION_FROM_E_ACCEPTED_RAW',
          scope='final64slice sum; frontend queries overlap directory queries; indexed updates are not additional CAM lookups'))
    return rows,provenance

def render_mechanisms(row,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    if any(row.get(s+'_mechanism_metrics') in [None,UNKNOWN] for s in ['baseline','variant']):return
    ms=[json.loads(row[s+'_mechanism_metrics']) for s in ['baseline','variant']]
    if any(not all(isinstance(m.get(k),dict) for k in ['trigger','local_service','bottleneck']) for m in ms):return
    fig,axes=plt.subplots(2,2,figsize=(10,6.2));fig.subplots_adjust(hspace=.55,wspace=.37,bottom=.14,top=.88)
    def bars(ax,labels,left,right,ylabel):
        xs=list(range(len(labels)))
        ax.bar([x-.18 for x in xs],left,.36,label='S',color='#777777')
        ax.bar([x+.18 for x in xs],right,.36,label='F',color='#416d86')
        ax.set_xticks(xs,labels);ax.set_ylabel(ylabel);ax.spines[['top','right']].set_visible(False)
    ax=axes[0,0];vals=[row['cycles_left'],row['cycles_right']]
    ax.bar(['S','F'],vals,color=['#777777','#416d86']);ax.set_ylabel('GPU cycles');ax.set_ylim(0,max(vals)*1.15)
    for n,v in enumerate(vals):ax.text(n,v+3500,f'{v:,}',ha='center',fontsize=9)
    ax.set_title('(a) Measured program time')
    bars(axes[0,1],['Copy read','Copy write','All grants'],
      [ms[0]['trigger']['logical_copy_reads']/1e6,ms[0]['trigger']['logical_copy_writes']/1e6,ms[0]['local_service']['physical_bank_grants']/1e6],
      [ms[1]['trigger']['logical_copy_reads']/1e6,ms[1]['trigger']['logical_copy_writes']/1e6,ms[1]['local_service']['physical_bank_grants']/1e6],
      'Operations (millions)')
    axes[0,1].set_title('(b) Local service; not GPU cycles');axes[0,1].legend(frameon=False)
    keys=['lower_read_bytes','lower_wb_bytes']
    bars(axes[1,0],['Lower reads','Lower WB'],*[ [m['local_service'][k]/1e6 for k in keys] for m in ms],'Traffic (decimal MB)')
    axes[1,0].set_title('(c) Net downstream traffic')
    reasons=['COPY_PIPELINE','WB_DATA_SPACE','DATA_SERVICE','MISS_QUEUE_FULL','LINE_MSHR_FULL','SAME_ADDRESS_WB']
    bars(axes[1,1],['Copy','WB space','Data','MissQ','MSHR','Same WB'],
      *[[m['bottleneck'][k]['request_wait_cycle_sum']/1e6 for k in reasons] for m in ms],
      'Request-cycles (millions)')
    axes[1,1].tick_params(axis='x',labelsize=7);axes[1,1].set_title('(d) Nonexclusive request waits')
    fig.suptitle(row['workload']+' | same binary '+row['binary'][:8]+' S/F | E accepted',fontsize=12)
    fig.text(.5,.035,'Waits overlap across requests, reasons and slices. No stacked stall decomposition.\n'
      'V/RO lookup waits are tabulated separately; module cycle contributions remain UNKNOWN.',ha='center',fontsize=9)
    for ext in ['pdf','png']:fig.savefig(out/(row['workload']+'_MECHANISMS.'+ext),dpi=180)
    plt.close(fig)

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
        else:
            label='输入HOLD' if result['main'][x]['status']=='HOLD_INPUT_SCIENTIFIC_SCOPE' else '待E接受'
            ax.text(x,.48*upper,label,ha='center',fontproperties=font,fontsize=9,color='#777777')
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
    p.add_argument('--binary',help='restrict direct E pair projection to this exact runtime SHA256')
    p.add_argument('--native-result-root',type=Path,default=Path('/workspace/ep_l2_ms20261019_e_results'))
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with (intake.SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock,fcntl.LOCK_SH)
        raw=(intake.SHARED/'RUN_REGISTRY.json').read_bytes();ledger=json.loads(raw)[intake.FIELD]
    if ledger.get('owner')!='E' or ledger.get('campaign_id')!=CAMPAIGN or ledger.get('authority_commit') not in [AUTH,intake.AUTHORITY]:
        raise ValueError('wrong canonical E ledger')
    # E may publish this optional, hash-bound display map with an event. No D
    # hand-written launch/qualification path exists, and no fallback matches by cycles.
    binding_ref=ledger.get('full_system_v2_analysis_bindings')
    binding=intake.pointer(binding_ref) if binding_ref else accepted_display_binding(ledger,a.binary)
    if binding and (binding.get('owner')!='E' or binding.get('authority')!=AUTH):
        raise ValueError('unreviewed/wrong-authority display map')
    hold_path=OUT.parent/'input_suitability_20261020_r1/INPUT_APPLICABILITY.json'
    holds=json.loads(hold_path.read_text()).get('holds',{}) if hold_path.exists() else {}
    result=views(ledger,binding,holds)
    (a.out/'E_PAIR_DISPLAY_PROJECTION.json').write_text(json.dumps(binding,indent=2)+'\n')
    mechanism_rows=[]
    for row in result['main']:
        if row['status']=='E_ACCEPTED_D_ANALYZED':
            mechanism_rows.extend(mechanism_table(row))
            costs,observations=terminal_cost_observations(ledger,row,a.native_result_root)
            mechanism_rows.extend(costs)
            (a.out/(row['workload']+'_COST_RAW_PROVENANCE.json')).write_text(json.dumps(observations,indent=2)+'\n')
            if a.render:render_mechanisms(row,a.out)
    # A withdrawal must remove the current data projection, while history and
    # older revision artifacts remain intact. Never leave a stale current CSV.
    csvout(a.out/'MECHANISM_MEASUREMENTS.csv',mechanism_rows,
      ['pair_id','workload','family','metric','S','F','F_minus_S','unit','scope','evidence_class'])
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
    (a.out/'CURRENT_ARTIFACTS.json').write_text(json.dumps({
      'current_pair_ids':[r['pair_id'] for r in result['main'] if r['status']=='E_ACCEPTED_D_ANALYZED'],
      'current_workloads':[r['workload'] for r in result['main'] if r['status']=='E_ACCEPTED_D_ANALYZED'],
      'older_history_and_files_are_not_current_acceptance':True,
      'paper_EN_v20_modified':False},indent=2)+'\n')
    print(json.dumps({k:v for k,v in result['summary'].items() if k!='RO_grid'}))

if __name__=='__main__':main()
