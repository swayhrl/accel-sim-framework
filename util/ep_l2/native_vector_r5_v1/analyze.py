#!/usr/bin/env python3
"""Project an already accepted native diagnostic without causal overreach."""
from pathlib import Path
import csv,json,hashlib
import vector_runtime as v
B=v.B
def main():
 point=v.read(B/'control'/('SCIENCE_QUALIFICATION_'+v.C+'.json'))
 assert point['status']=='EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED' and point['pair'] is False
 out=B/'run/results'/point['uuid']
 model=v.read(out/'terminal_summary.json');old=v.read(out/'R4_212_TERMINAL.json');new=v.read(out/'R5_TAGPRESSURE_TERMINAL.json')
 wire=v.read(B/'sources/r5/WIRE_CONTRACT.json');rawlabels=wire['raw_labels']
 h=new['global_record']['histograms'];gc=new['global_record']['counters'];oc=old['global_counters']
 miss=rawlabels.index('MISS');fail=rawlabels.index('RESERVATION_FAIL')
 selected={miss,fail}
 heads=h['heads_raw_reserved'];eligible=h['heads_raw_reserved_eligible']
 ro=model['mechanism_metrics']['full_mechanism_records']['readonly']
 counts={name:sum(row['summary'][name] for row in ro.values()) for name in ['accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','responses','detached']}
 prod={name:oc[name] for name in ['ft_access_attempts','commit_raw_probe_reached','raw_tag_fail_commit','relieve_calls','relieve_T_disabled','relieve_no_eligible','relieve_eligible_selected','detach_calls','detach_success','detached_retired','trigger_accepted_after_detach','trigger_denied_after_detach']}
 data={'schema':'EP_MAIN_VECTOR_R5_ACCEPTED_CAUSE_PROJECTION_V1','accepted_point_sha256':v.sha(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'),'pair':False,'counts_unit_warning':'RO counters are requests/transactions; occupancy/eligible histograms are covered head-cycle exposures; no multiplication of marginals','RO':counts,'r5_head_cycle_coverage':gc,'raw_by_target_reserved':heads,'maximum_reserved_ways_covered':max((r[1] for r in heads),default=None),'maximum_reserved_ways_new_tag_demand':max((r[1] for r in heads if r[0] in selected),default=None),'tag_ways':16,'new_tag_head_cycle_exposures':sum(r[-1] for r in heads if r[0] in selected),'all16_reserved_new_tag_head_cycle_exposures':sum(r[-1] for r in heads if r[0] in selected and r[1]==16),'raw_FAIL_head_cycle_exposures':sum(r[-1] for r in heads if r[0]==fail),'structural_eligible_head_cycle_exposures':sum(r[-1] for r in eligible if r[2]>0),'new_tag_and_structural_eligible_joint_head_cycle_exposures':sum(r[-1] for r in eligible if r[0] in selected and r[2]>0),'actual_production_commit_domain':prod,'cycles':point['cycles'],'instructions':point['instructions'],'wall_seconds':point['wall_seconds'],'source_identity':point['source_identity'],'source_keep':True,'skipped_raw_dimensions':'NA_NOT_OBSERVED','kernel_phase_semantics':'Physical event-time labels, not requester/victim causal ownership','numeric_SASS_output_validation':'UNKNOWN','no_old_main61_or_other_binary_performance_pair':True}
 if counts['transactions']==0:category='NO_RO_TRANSACTION_AT_THIS_POINT'
 elif prod['raw_tag_fail_commit']==0 and data['all16_reserved_new_tag_head_cycle_exposures']==0:category='TRIGGER_ABSENCE_IN_COVERED_AND_PRODUCTION_DOMAINS'
 elif prod['detach_success']>0 and prod['detached_retired']==prod['detach_success']:category='DETACH_ACTIVATED_WITH_LIFECYCLE_CLOSURE_NO_ISOLATED_PERFORMANCE_CLAIM'
 elif data['raw_FAIL_head_cycle_exposures']>0 and data['structural_eligible_head_cycle_exposures']==0:category='PRESSURE_WITHOUT_STRUCTURAL_ELIGIBILITY_IN_COVERED_DOMAIN'
 else:category='PRESSURE_OR_ELIGIBILITY_REQUIRES_SCOPED_GATE_ANALYSIS'
 data['outcome']=category
 v.put(out/'SCIENTIFIC_CAUSE_PROJECTION.json',data)
 with (out/'COVERED_TARGET_SET_HISTOGRAM.csv').open('x',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['raw_status','reserved_ways','covered_head_cycle_exposures'])
  for raw,r,n in heads:w.writerow([rawlabels[raw],r,n])
 report=f"""# Vector r5 原生验证结果

科学接受：{point['status']}。完整应用1次，无自动重试；独立诊断点，非S/F性能配对。

| 项目 | 已接受值 |
|---|---:|
| 模拟周期 | {point['cycles']} |
| 完整指令 | {point['instructions']} |
| kernel / slice | 1 / 64 |
| 墙钟秒 | {point['wall_seconds']:.3f} |
| RO事务 | {counts['transactions']} |
| RO合并请求 | {counts['merges']} |
| 已接受RO请求/响应 | {counts['accepted_ro']} / {counts['responses']} |
| 实际生产TagFAIL | {prod['raw_tag_fail_commit']} |
| 实际relieve / detach / detached退休 | {prod['relieve_calls']} / {prod['detach_success']} / {prod['detached_retired']} |
| covered目标set最大RESERVED | {data['maximum_reserved_ways_covered']} / 16 |
| 新Tag需求域最大RESERVED | {data['maximum_reserved_ways_new_tag_demand']} / 16 |
| covered新Tag需求head-cycle | {data['new_tag_head_cycle_exposures']} |
| 其中all16 RESERVED | {data['all16_reserved_new_tag_head_cycle_exposures']} |
| structural eligible head-cycle | {data['structural_eligible_head_cycle_exposures']} |
| 新Tag需求与eligible的实际联合head-cycle | {data['new_tag_and_structural_eligible_joint_head_cycle_exposures']} |

结果分类：{category}。

本点的结论严格限于源绑定的生产FT/RO调用域与已探测head-cycle。TVD等skipped域保持NA，不外推为零压力；存在RO对象、eligible或满VALID/MODIFIED occupancy均不自动构成不可替换Tag压力。head-cycle不是独立请求，物理phase不是requester/victim的kernel因果身份。

若本点为触发缺失，T的真实应用收益声明应收紧。Conv仍未运行，是否追加需下一项单独科学决策，本Goal不自动继续。即使观察到detach，也需同binary受控T-OFF验证才能识别独立性能收益。

实际source为Core1093/main e511；旧main61的S/F、原57/T0、失败/HOLD和已接受配对保持各自身份。没有重新编译或改动有限模型，也不主张SASS数值输出验证或硬件速度收益。全模型闭合、ROC1、64slice、固定212、新r5联合数学、完整真实进程退出已分别通过；具体SHA和证据见同目录JSON。

结果按COPY_ONLY归档真164及独立native Target恢复后，归档回执另行记录。源原件KEEP。
"""
 (out/'SCIENTIFIC_REPORT.md').write_text(report)
 return data
if __name__=='__main__':print(json.dumps(main(),ensure_ascii=False,indent=2))
