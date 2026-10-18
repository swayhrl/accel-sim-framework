#!/usr/bin/env python3
"""Render compact tables from this revision's identity-checked derivation."""
import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--derived', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = list(csv.DictReader((args.derived / 'finite_service_metrics.csv').open()))
    # This narrative is a frozen first-checkpoint report. A later result event
    # must create a new revision rather than silently retaining these counts.
    assert json.loads((args.derived / 'AUTHORITY.json').read_text())['scientific_acceptance']['generation'] == 47
    assert len(rows) == 46 and all(r['pin_block'] == r['pool_full'] == '0' for r in rows)
    current = [r for r in rows if r['binary'].startswith('fb67448d') and r['condition'] == 'H0' and r['workload'] in ('convolutionSeparable', 'FWT_7_21')]
    assert len(current) == 8
    historical = [r for r in rows if r['binary'].startswith('23094a9d') and r['condition'] == 'H0']
    assert len(historical) == 10
    assert all(r['pin_block'] == r['pool_full'] == '0' for r in historical)
    assert all(r['bank_grants'] == r['bank_logical_ops'] and r['wb_created'] == r['wb_completed'] == r['wb_lower_accept'] for r in rows)
    assert all(all(r[k] == '0' for k in ('reserved', 'read_refs', 'wb_slots', 'wb_live')) for r in rows)
    keys = ['workload', 'profile', 'cycles', 'pin_block', 'pool_full', 'wbuf_full', 'WB_record_peak', 'WAD_peak',
            'c7d_wad_full_events', 'c7d_wad_hazard_events', 'c7d_missq_full_block', 'c7d_l2_to_dram_full_block',
            'c7d_dram_scheduler_full_block', 'c7d_dram_issue_eligible', 'bank_retry_attempts', 'bank_wait_cycles']
    def table(selected):
        return '| ' + ' | '.join(keys) + ' |\n|' + '|'.join('---' for _ in keys) + '|\n' + ''.join('| ' + ' | '.join(r[k] or 'N/A' for k in keys) + ' |\n' for r in selected)
    text = '''# 已接受机会背景：原始计数与范围

generation47；每条raw SHA与接受row、独立review SHA一致，使用最后一组application累计/FT每slice记录，未把多次kernel边界打印相加。46个有限路径raw全部保留为derived行，含零/负性能点；另5个Ideal端点只列catalog，不用于有限机会推断。raw未输出M0/L2CHAR专用观测时保留null，不能当真实0。

## 同binary四模式（combined fb67448d，H0）

''' + table(sorted(current, key=lambda r: (r['workload'], r['profile']))) + '''
`wbuf_full`、WAD full/hazard、MissQ full是不同控制边界的计数。bank重试是调用次数，bank_wait是各logical-op等待间隔之和；不同slice/请求重叠，不能相加为独占GPU stall。WAD-full与same-address hazard是独立预检谓词；不能把其和当一个消除后可直接兑现的时间。`c7d_l2_to_dram_full_block`在`!admit && plan.will_send_lower_read && lowerq.full()`时增加，是frontend伴随条件，不是所有MissQ head drain的精确拒绝数，更不是MQ2机会计数。scheduler-full按真实DRAM issue-attempt观测，不是GPU时间分母。

## 原H0五输入（binary23094a9d，不替换原五输入结论）

''' + table(historical) + '''
这10行pin_block=pool_full=0。全部46行这两项亦为0，但只表示这些实际counter未激活，不证明所有可能frontend等待已完整覆盖。不优先开发pin-aware victim或跨bank任意landing。46行终态created=lower_accept=completed，logical_ops=grants，reserved/read_refs/wb_slots/wb_live=0；终态闭合不排除中间retained-grant空转。

## 既有受控正负例

Conv Q4 B/U为290333/293709，S_EP=0.988505630；WAD256_Q4为292132/289899，S_EP=1.007702683。WAD-full计数55645/54516降为0/0。该metadata控制有实测交互，但不是MQ2/RG1结果、不是任意输入可兑现的critical-path贡献。Conv D4中U bank_wait从1962721降至1791989而cycles由B267521到U268544变慢；少重试/少等待不能替代实测效果。CFD H0负例与所有其它有限背景仍保留在CSV。

`window_availability_summary.csv`汇总169472条原5000-cycle slice-window记录（46行导出）；其中正占用与bank等待共处一个窗口，只是粗粒度共存，不证明相同cycle相同请求的ready/blocked关系。整数平均为0也不证明窗口里队列从未非空。
'''
    (args.out / 'ACCEPTED_RAW_OBSERVATIONS.md').write_text(text)
    four = list(csv.DictReader((args.derived / 'four_mode_OFF_context.csv').open()))
    text = '''# 四模式对照对本轮的约束

本表是已经接受的combined发行背景，不是新microopt的OFF/ON结果。Core9bd30ed、Framework8ab6013、binaryfb67448d的完整身份与run-key在CSV。

| 输入 | C_B | C_S64 | C_U_CAP16 | C_U | B/U | S64/U | U_CAP16/U |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in four:
        text += '| ' + ' | '.join([r['workload'], r['C_B'], r['C_S64'], r['C_U_CAP16'], r['C_U'], *(f'{float(r[k]):.9f}' for k in ('S_EP', 'S_static', 'U_capacity_marginal'))]) + ' |\n'
    text += '''
观察：增加静态WB从16到64没有使两个样本变快；S64比B16分别慢326/1438cycles。Unified相对U_CAP16分别快1019/34cycles（0.3495%/0.0069%的ratio增益），容量边际明显依输入变化。S64 observed wbuf_full为0、record峰值58/35，没有证明静态预算对所有输入非约束，也没有证明该分区是最优静态。S64不是额外48行的免费容量，128bypass减少为80；总payload1168不变。

竞争解释：B16→U_CAP16同时改变in-place/copy、payload角色组织与落点；不是纯copy单因素。U_CAP16→Unified保持统一组织而去掉local reserved+live≤16限制，较接近容量边际，但schedule/下游队列随其变化，不能把cycle差进一步无证据拆成独占阻塞。FWT在U_CAP16有967460次quota refusal而放开仅快34cycles，正好约束“refusal次数就是性能收益”的错误叙述。

受控对照：本轮要求B16/S64/Unified各自OFF→MQ2/RG1；四模式给出已有归因背景，不能跨新binary沿用这些OFF。保留同背景的Q4/WAD256、D2/D4及ICNT2正负例；不追加全扫。

结论范围：当前已接受数据支持统一组织相对这两个静态分区的有限优势，以及Conv比FWT更可见的容量边际；尚不能声称MQ2/RG1会扩展EP收益。局部/完整Ideals属于另有scope的端点，不是本轮服务回收机会的实测上界，也不跨binary拼成分解。
'''
    (args.out / 'FOUR_MODE_CONTEXT.md').write_text(text)
    print(json.dumps(dict(status='PASS_REPORT_BINDING', finite_rows=len(rows), combined_four_mode_rows=len(current), original_H0_rows=len(historical), terminal_checks=46)))


if __name__ == '__main__':
    main()
