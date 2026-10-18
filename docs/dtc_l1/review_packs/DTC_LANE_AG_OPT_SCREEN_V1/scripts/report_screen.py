#!/usr/bin/env python3
"""Report only this cohort's exact reservations; no historical performance fill."""
from common import *
from define_metrics import DEFINITIONS
from fractions import Fraction
import re

def value(result,key):
 if not result or not result.get('performance_accepted'):return 'UNAVAILABLE'
 if key.startswith('traffic.'):return result.get('traffic',{}).get(key.split('.',1)[1],'UNAVAILABLE')
 return result.get('final_metrics',{}).get(key,'UNAVAILABLE')

def main():
 manifest=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
 specs=[json.loads((PACK/p).read_text()) for p in manifest['ordered_specs']]
 matrix=json.loads((RAW/'MATRIX_TERMINAL.json').read_text()) if (RAW/'MATRIX_TERMINAL.json').exists() else None
 data={};paths={};starts=budget=0
 for spec in specs:
  run=RAW/'attempts'/(spec['point']+'_'+spec['attempt_uuid']);paths[spec['point']]=run
  budget+=int((run/'RUN_START.json').exists());starts+=int((run/'POPEN_CHILD.json').exists())
  if (run/'STRICT.json').exists():data[spec['point']]=json.loads((run/'STRICT.json').read_text())
 bases={w:data.get('BASE_'+w) for w in ['GEMM','Gaussian']}
 rows=[];metrics=[];diagnostics=[]
 diag_keys=['samples','eligible_ready_sum','eligible_ready_cycles','collect_idle_eligible_cycles','overlap_cycles',
     'result_occupancy_samples','collecting_occupancy_samples','result_backpressure_cycles',
     'wb_arbitration_blocked_cycles','wb_attempts','wb_denied_attempts','collected_sectors','retires']
 for spec in specs:
  point=spec['point'];run=paths[point];r=data.get(point);base=bases[spec['workload']]
  accepted=bool(r and r.get('performance_accepted'));calibrated=bool(base and base.get('performance_accepted'))
  cycles=r['cycles'] if accepted else 'UNAVAILABLE'
  if accepted:assert isinstance(cycles,int) and not isinstance(cycles,bool)
  ratio=Fraction(cycles,base['cycles']) if accepted and calibrated else None
  status=(r['status'] if r else 'HOLD_UNQUALIFIED' if spec['qualification']=='HOLD_UNQUALIFIED' else
      'NOT_STARTED_COHORT_STOP' if matrix else 'RUNNING_OR_PENDING' if (run/'RUN_START.json').exists() else 'NOT_STARTED')
  row=dict(order=spec['order'],point=point,attempt_uuid=spec['attempt_uuid'],status=status,
      budget_consumed=int((run/'RUN_START.json').exists()),actual_Popen_child=int((run/'POPEN_CHILD.json').exists()),
      strict_accepted=accepted,integer_cycles=cycles,cycle_ratio_to_this_input_AG_BASE=str(ratio) if ratio else 'UNAVAILABLE',
      cycle_ratio_decimal=format(float(ratio),'.9f') if ratio else 'UNAVAILABLE',
      BASE_over_arm_ratio=str(1/ratio) if ratio else 'UNAVAILABLE',
      kernels=r.get('kernels','UNAVAILABLE') if r else 'UNAVAILABLE',
      active_instructions=r.get('active_instructions','UNAVAILABLE') if r else 'UNAVAILABLE',
      CTA=r.get('CTA','UNAVAILABLE') if r else 'UNAVAILABLE',
      reason=r.get('failure','') if r else spec['qualification_reason'] if spec['qualification']=='HOLD_UNQUALIFIED' else matrix.get('reason','') if matrix else 'Await published registration and fresh admission',
      raw=str(run) if run.exists() else 'NOT_CREATED',historical_result_used=False)
  rows.append(row)
  for field,key,unit,denom,definition in DEFINITIONS:
   numerator=value(r,key) if key!='UNAVAILABLE' else 'UNAVAILABLE'
   if denom!='1':
    denominator=value(r,denom)
    measured=str(Fraction(numerator,denominator)) if isinstance(numerator,int) and isinstance(denominator,int) and denominator else 'UNDEFINED_ZERO_DENOMINATOR' if denominator==0 else 'UNAVAILABLE'
   else:measured=numerator
   metrics.append(dict(point=point,field=field,value=measured,unit=unit,source_key=key,
       comparable='SAME_DEFINITION_PUBLIC_ONLY' if isinstance(numerator,int) else 'UNAVAILABLE',
       scope='LAST_COMPLETE_CUMULATIVE_SNAPSHOT_NOT_SUM_OF_KERNELS'))
  diag=r.get('AC_pipeline_diagnostic',{}) if accepted else {}
  totals=diag.get('cumulative_sums',{})
  for key in diag_keys:
   diagnostics.append(dict(point=point,field=key,value=totals.get(key,'UNAVAILABLE'),
       availability='ON_ONLY_NONCOMPARATIVE' if key in totals else 'UNAVAILABLE_NOT_PRINTED_OR_NOT_ACCEPTED',
       direct_OFF_comparison=False))
 table(PACK/'RESULTS.tsv',rows);table(PACK/'COMMON_METRICS.tsv',metrics);table(PACK/'AC_ON_DIAGNOSTICS.tsv',diagnostics)
 state='CPU_QUALIFIED_PREREGISTRATION_NOT_YET_EXECUTED' if not matrix and budget==0 else matrix['status'] if matrix else 'RUNNING'
 summary=dict(utc=now(),cohort='DISCOVERY_OPT',status=state,budget_cap=8,budget_consumed=budget,
     verified_Popen_children=starts,full_strict_passes=sum(r.get('performance_accepted',False) for r in data.values()),
     fixed_slots=8,HOLD_UNQUALIFIED=2,AA5_actual_starts=1,AA5_full_strict_passes=0,
     source_core=manifest['combined_core_commit'],matrix_terminal=matrix,
     rows=rows,ratios_only_new_common_BASE=True,GM12=False,manuscript_modified=False)
 write(PACK/'RESULT_SUMMARY.json',summary)
 lines=['# AG DISCOVERY_OPT — '+state,'',
     f'新模拟实际Popen child {starts}；保守启动预算消耗 {budget}/8；完整strict PASS {summary["full_strict_passes"]}。固定八格，AD两格HOLD_UNQUALIFIED，不替换、不补跑。',
     '', '| 点 | 状态 | 整数cycles | arm / 本轮同输入BASE |', '|---|---|---:|---:|']
 lines += [f'| {r["point"]} | {r["status"]} | {r["integer_cycles"]} | {r["cycle_ratio_to_this_input_AG_BASE"]} |' for r in rows]
 lines += ['', 'Core `'+manifest['combined_core_commit']+'`；固定X2上只合入AC83aca449与AEae83cc51，AD未资格、AF排除。15/15 CTest、AE137、AC80、68个AC×AE实际LDST CPU交错、正常导出/OFF差分/全echo资格见QUALIFICATION_DECISION.json。AC额外160KiB/SM明确收费，不是equal-area。',
     '', 'BASE仅以本轮全输入自然exit0+strict及旧完整K0共同定义指标严格校准成立；旧T数值只作参照，不能填本轮表。两输入是发现集，不能声称独立验证或计算原GM12；host wall不推GPU性能。',
     '', 'AA5历史保持1/4实际启动、0/4完整strict；旧UUID d0a29a82-c171-46e4-b077-d7ccfd2c4b7a在451.4s按冻结合同因host pswpin+1page STOP，仅67/510，own majorfault0。原STOP/raw/UUID未修改、未重启，不作校准。',
     '', '共同计数、PIB/physical积分、lower/L2/DRAM实际单位见COMMON_METRICS.tsv；AC真实collection/WB重叠等只列AC_ON_DIAGNOSTICS.tsv。OFF未打印、K1-only、hash set/bank直方图及逐消费者时序均UNAVAILABLE，不补零。无native值正确性结论。',
     '', '资源合同AG_DISCOVERY_RESOURCE_R2_V1：单sim；孤立host-global页变化WARN并加密采样；新增OOM、最低线、持续swap/PSI仍STOP。每次新准入/全FLOCK与真实loader库身份、监测和原始失败日志保存在独立AG raw。']
 if matrix:lines += ['', '终态原因：`'+str(matrix.get('reason'))+'`。无重试、retune、补格或后续自动派发。']
 else:lines += ['', '完整预注册push/fetch-back及每次新准入是发射前提；本CPU审查状态本身不表示已执行性能。']
 (PACK/'LATEST_REPORT.md').write_text('\n'.join(lines)+'\n')
 f=PACK/'MEASURED_VS_INFERRED.md';s=f.read_text()
 paragraph=f'本轮性能实测：实际Popen child {starts}，预算消耗{budget}/8，完整strict PASS {summary["full_strict_passes"]}；各点整数cycles与仅对本轮同输入BASE的比值见RESULTS.tsv。未通过完整strict者不报告性能cycles，原始prefix仅保存在失败raw。两输入仍为发现集，host wall永不作GPU速度，不替代独立验证、GM12或旧AA5四格。'
 s=re.sub(r'^(?:未测性能：|本轮性能实测：)[^\n]*',paragraph,s,flags=re.M);f.write_text(s)
 print(json.dumps(dict(status=state,budget=budget,actual_children=starts,strict_passes=summary['full_strict_passes'])))

if __name__=='__main__':main()
