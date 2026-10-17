"""Publish all seven registered outcomes and the fixed two-discovery-input score."""
import math
from common import *


def main():
    with (PACK/'PRE_REGISTRATION.tsv').open() as f:plan=list(csv.DictReader(f,delimiter='\t'))
    controls=json.loads((PACK/'ACCEPTED_CONTROLS.json').read_text())
    status=json.loads((ROOT/'STATUS.json').read_text()) if (ROOT/'STATUS.json').exists() else {}
    rows=[]
    for point in plan:
        uid=point['attempt_uuid']
        spec=json.loads(Path(point['spec_path']).read_text())
        strictfile=ROOT/(uid+'.strict.json')
        run=ROOT/'attempts'/(point['label']+'_'+uid)
        row=dict(candidate=point['candidate'],workload=point['workload'],attempt_uuid=uid,
                 status='NOT_LAUNCHED_'+str(status.get('halted') or 'PENDING_GATES'),
                 cycles='',instructions='',original_oo_cycles=controls[point['workload']+'_OO128']['cycles'],
                 original_cplus_cycles=controls[point['workload']+'_CPLUS']['cycles'],
                 R_original_OO_over_new='',original_CPLUS_over_new='',max_rss_kib='',
                 elapsed_wall='',stdout_sha256='',strict_sha256='',raw_dir=str(run))
        if strictfile.exists():
            result=json.loads(strictfile.read_text())
            row.update(status=result['status'],strict_sha256=sha(strictfile))
            base=result['base']
            for key in ['cycles','instructions','stdout_sha256','elapsed_wall']:
                row[key]=base[key]
            row['max_rss_kib']=base['max_rss_kb']
            if result['status']=='PASS_STRICT_EXPLORATORY_SCOPE':
                row['R_original_OO_over_new']=row['original_oo_cycles']/int(row['cycles'])
                row['original_CPLUS_over_new']=row['original_cplus_cycles']/int(row['cycles'])
            (PACK/'strict').mkdir(exist_ok=True)
            dest=PACK/'strict'/strictfile.name
            if dest.exists():assert dest.read_bytes()==strictfile.read_bytes()
            else:dest.write_bytes(strictfile.read_bytes())
        elif (run/'RUN_START.json').exists():
            row['status']='RUNNING' if not (run/'RUN_TERMINAL.json').exists() else 'TERMINAL_UNACCEPTED_PRESERVED'
        elif point['label'] in status.get('terminal',{}):
            row['status']=status['terminal'][point['label']]
        rows.append(row)
    assert len(rows)==7
    # Re-running a publication with changed current status must use a new
    # checkpoint, never overwrite a previously accepted outcome table.
    table(PACK/'FULL_MATRIX.tsv',rows)
    scores=[]
    for candidate in ['T1-A','T1-B','T1-C']:
        pair=[r for r in rows if r['candidate']==candidate]
        passed=len(pair)==2 and all(r['status']=='PASS_STRICT_EXPLORATORY_SCOPE' for r in pair)
        ratios=[r['R_original_OO_over_new'] for r in pair] if passed else []
        minimum=min(ratios) if passed else ''
        gm=math.sqrt(math.prod(ratios)) if passed else ''
        scores.append(dict(candidate=candidate,gemm_status=next(r['status'] for r in pair if r['workload']=='GEMM'),
                           gaussian_status=next(r['status'] for r in pair if r['workload']=='Gaussian'),
                           R_GEMM=next(r['R_original_OO_over_new'] for r in pair if r['workload']=='GEMM'),
                           R_Gaussian=next(r['R_original_OO_over_new'] for r in pair if r['workload']=='Gaussian'),
                           R_min=minimum,R_g=gm,
                           eligible=passed and minimum>=0.98 and gm>=1.02,
                           selected=False,
                           mappings=int(next(p for p in plan if p['candidate']==candidate)['logical_sets'])*int(next(p for p in plan if p['candidate']==candidate)['logical_ways']),
                           ways=int(next(p for p in plan if p['candidate']==candidate)['logical_ways'])))
    eligible=[s for s in scores if s['eligible']]
    selected=None
    if eligible:
        best=max(s['R_g'] for s in eligible)
        tied=[s for s in eligible if (best-s['R_g'])/best<0.005]
        selected=min(tied,key=lambda s:(s['mappings'],s['ways']))['candidate']
        for s in scores:s['selected']=s['candidate']==selected
    table(PACK/'DISCOVERY_SCORE.tsv',scores)
    summary=dict(status='T1_CANDIDATE_FOR_REVIEW_ONLY' if selected else 'NO_QUALIFIED_TAG_PROMOTION_IN_T1',
                 selected=selected,strict_pass=sum(r['status']=='PASS_STRICT_EXPLORATORY_SCOPE' for r in rows),
                 registered=7,actually_launched=len(status.get('launched',[])),
                 all_outcomes_included=True,holdout_runs=0,t2_runs=0,new_mechanisms=0,
                 selection_policy_sha256=sha(PACK/'POLICY.json'),
                 input_scope='TWO_PREREGISTERED_DISCOVERY_INPUTS_NOT_PAPER_GM12',utc=now())
    write(PACK/'EXPLORATION_SUMMARY.json',summary)
    # Small execution and authority receipts are publishable. Keep raw in ROOT.
    for name in ['PRE_REG_FETCH_BACK.json','M_CONSUMPTION.json','EXECUTION_GATE.json',
                 'AUTHORITY_ACTIVE.json','AUTHORITY_TERMINAL.json','STATUS.json']:
        src=ROOT/name
        if src.exists():
            dest=PACK/name
            if dest.exists():assert dest.read_bytes()==src.read_bytes()
            else:dest.write_bytes(src.read_bytes())
    raw=[]
    for r in rows:
        d=Path(r['raw_dir'])
        if d.exists():
            for name in ['RUN_START.json','RUN_TERMINAL.json','SPEC.json','simulator.stdout',
                         'simulator.stderr','resource.time','PID.json','immutable_runner.py']:
                file=d/name
                if file.exists():raw.append(dict(attempt_uuid=r['attempt_uuid'],path=str(file),bytes=file.stat().st_size,sha256=sha(file)))
    if raw:table(PACK/'RAW_FILES_SHA256.tsv',raw)
    t0=rows[0]
    t0line=(f"T0 GEMM IO128: {t0['status']}, cycles={t0['cycles'] or 'NA'}；"
            f"原IO256={controls['GEMM_IO256']['cycles']}、OO128={controls['GEMM_OO128']['cycles']}。")
    report=f"""# Lane T — bounded Tag/PIB pilot final report

{summary['status']}。严格通过 {summary['strict_pass']}/7，实际启动 {summary['actually_launched']}/7。胜出候选：{selected or '无'}；全部失败、HOLD及负收益在完整矩阵保留。

{t0line}

仅对GEMM/Gaussian两个固定发现输入，R=原OO128周期/新OO周期，按预注册min≥0.98、GM≥1.02和同一全局候选规则选择。详见FULL_MATRIX.tsv、DISCOVERY_SCORE.tsv及逐UUID strict收据。GM是探索评分，不是主论文总体加速；T0不参加Tag候选选择。

资源：每点/usr/bin/time -v记录峰值RSS及实际墙钟；完整配置、额外Tag映射/比较开销、固定80KiB池/16KiB普通side/96KiB shared见RESOURCE_OVERHEAD.tsv。1cycle Tag是未综合的探索假设，无硬件等频/等面积资格。

原44行、Core、trace、parser、旧UUID和baseline均未修改；没有运行holdout、T2、128KiB modern或新机制。T1到此收口，后续只能审查是否值得单一候选holdout及PPA，不自动启动。

原174 raw：{ROOT}。预注册提交及fetch-back、M消费、执行门槛和authority收据随包保存。指标缺口及科学边界见SCIENTIFIC_SCOPE.md。本报告不把UNAVAILABLE字段补造成通过证据。
"""
    with (PACK/'LATEST_REPORT.md').open('x') as f:f.write(report)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    main()
