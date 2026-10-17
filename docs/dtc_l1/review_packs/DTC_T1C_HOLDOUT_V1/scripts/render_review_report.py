"""Render already-audited terminal data; preserve the fixed two-holdout contract."""
from common import *
from datetime import timedelta


def read_table(name):
    with (PACK / name).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def number(value, decimals=3, signed=False):
    if value in ('', 'UNAVAILABLE', 'UNCOMPARABLE', None):
        return str(value or 'UNAVAILABLE')
    if decimals == 0:
        return format(int(value), ',')
    return format(float(value), ('+' if signed else '') + ',.' + str(decimals) + 'f')


def main():
    terminal = json.loads((ROOT / 'AUTHORITY_TERMINAL.json').read_text())
    assert not terminal['final']['active']
    authority = json.loads((ROOT / 'AUTHORITY_ACTIVE.json').read_text())
    current = proc(authority['pid'])
    assert not current or current['state'] == 'Z' or current['start_ticks'] != authority['start_ticks']
    audit = json.loads((PACK / 'FINAL_CONTRACT_AUDIT.json').read_text())
    assert audit['status'] == 'PASS_TERMINAL_CONTRACT_AND_IDENTITY_AUDIT'
    matrix = read_table('FULL_MATRIX.tsv')
    mechanisms = read_table('TERMINAL_MECHANISM_COMPARISON.tsv')
    resources = read_table('EXECUTION_RESOURCES.tsv')
    resource_summary = json.loads((PACK / 'RESOURCE_EXECUTION_SUMMARY.json').read_text())
    prereg = json.loads((PACK / 'PRE_REG_FETCH_BACK.json').read_text())
    selected = [r for r in matrix if r['arm'] == 'FIXED_T1C']
    assert len(matrix) == 6 and len(selected) == len(resources) == 2
    lines = ['# 固定 T1-C：DWT2D / BICG 独立 holdout 审查包', '',
        '本轮验证预先固定的 T1-C（OO128，64 sets × 8 ways），两个原完整输入各一次实际启动。'
        '两输入未参与 T1-C 选型，旧 OO/C+ baseline 已知。逐输入报告全部结果，不进行新选型、'
        'holdout GM 或论文主配置晋升。', '',
        '| 输入 | 原 OO 周期 | 原 C+ 周期 | 固定 T1-C 周期 | R_OO | R_CPLUS | 对 OO 周期变化 | 对 C+ 周期变化 | 新点验收 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for row in selected:
        lines.append('| ' + ' | '.join([
            row['workload'], number(row['accepted_original_oo_cycles'], 0),
            number(row['accepted_original_cplus_cycles'], 0), number(row['cycles'], 0),
            number(row['R_OO'], 6), number(row['R_CPLUS'], 6),
            number(row['cycles_change_vs_OO_pct'], signed=True) + '%',
            number(row['cycles_change_vs_CPLUS_pct'], signed=True) + '%', row['status']]) + ' |')
    lines += ['', 'R_OO = 原 OO 周期 / 新周期；R_CPLUS = 原 C+ 周期 / 新周期。'
        '周期变化 = (新周期 / 对照周期 − 1) × 100%，正数代表周期增加。'
        '不完整点的正式速度比保持空值。完整六臂、UUID 和 stdout SHA 见 [FULL_MATRIX.tsv](FULL_MATRIX.tsv)。', '']
    for workload in ['DWT2D', 'BICG']:
        rows = {r['point']: r for r in mechanisms if r['workload'] == workload}
        lines += [f'## {workload}：终态机制与同路径计数', '',
                  '| 字段 / 单位 | 原 OO128 | 固定 T1-C | 原 C+ |',
                  '| --- | ---: | ---: | ---: |']
        fields = [
            ('ready reference outcomes / 128B refs', 'ready_reference_outcomes', 0),
            ('pending reference outcomes / 128B refs', 'pending_reference_outcomes', 0),
            ('new allocation outcomes / 128B refs', 'new_allocation_outcomes', 0),
            ('accepted reference count / 128B refs', 'accepted_128b_reference_count', 0),
            ('ready fraction / accepted refs', 'ready_fraction', 6),
            ('pending fraction / accepted refs', 'pending_fraction', 6),
            ('new fraction / accepted refs', 'new_fraction', 6),
            ('DTC lower created / 128B requests', 'dtc_lower_created', 0),
            ('Tag evictions / count', 'tag_evictions', 0),
            ('PIB residency / all-64SM cycle mean', 'all64sm_cycle_mean_pib', 6),
            ('physical residency / all-64SM cycle mean', 'all64sm_cycle_mean_physical', 6),
            ('ready-to-collect / cycles per retired cacheable warp', 'ready_to_collect_per_cacheable_warp', 6),
            ('collection / cycles per retired cacheable warp', 'collection_per_cacheable_warp', 6),
            ('fully-ready-to-complete / cycles per retired cacheable warp', 'fully_ready_to_complete_per_cacheable_warp', 6),
            ('L2 read sectors / 32B sectors', 'L2_read_sectors', 0),
            ('DRAM read payload / bytes', 'DRAM_read_payload_bytes', 0),
            ('DRAM write payload / bytes', 'DRAM_write_payload_bytes', 0),
        ]
        for title, field, decimals in fields:
            values = [number(rows[arm].get(field) if arm in rows else None, decimals)
                      for arm in ['ORIGINAL_OO128', 'FIXED_T1C', 'ORIGINAL_CPLUS']]
            lines.append('| ' + ' | '.join([title, *values]) + ' |')
        if 'FIXED_T1C' in rows:
            lines += ['', 'L2/DRAM 可比性：`' + rows['FIXED_T1C']['L2_DRAM_comparability'] + '`。']
        lines.append('')
    lines += ['两个固定 holdout 的周期均低于原 OO：DWT2D 改善幅度很小，BICG 改善幅度较大。'
        '但 BICG 仍比原 C+ 增加62.334%周期；这项负收益完整保留，不能据此建立普适优越性或替换论文主配置。'
        'DWT2D 的新增分配减少伴随极小的 DRAM read payload 变化；BICG 的新增分配计数变化很小，'
        'DRAM read payload 变化更大，且 ready-to-collect 与 fully-ready-to-complete 条件均值上升。'
        '这些现象描述同一固定模型下的共现变化，尚无可加的整机周期归因。', '',
        '以上计数比较描述同一定义下的变化；不把 credit 转换成 DRAM 字节，'
        '不把条件服务均值差当作可加的整机周期贡献。C+ 无 DTC 路径字段标 UNAVAILABLE。'
        'L2/DRAM 采用 Lane M 已冻结的单 stream、终态、controller 和 atom 单位检查；'
        '不能闭合时标 UNCOMPARABLE。详细定义、分母及来源见 '
        '[TERMINAL_MECHANISM_COMPARISON.tsv](TERMINAL_MECHANISM_COMPARISON.tsv) 和 '
        '[METRIC_COMPARABILITY_EVIDENCE.json](METRIC_COMPARABILITY_EVIDENCE.json)。', '',
        '## 执行资源与硬件成本边界', '',
        '| 输入 | wall | user 秒 | system 秒 | 最大 RSS KiB |',
        '| --- | ---: | ---: | ---: | ---: |']
    for row in resources:
        lines.append('| ' + ' | '.join([row['workload'], row['elapsed_wall'],
            row['user_seconds'], row['system_seconds'], number(row['max_rss_kib'], 0)]) + ' |')
    summary = resource_summary
    lines += ['',
        f"资源样本 {summary['sample_count']} 份，最大采样间隔 {summary['largest_sample_gap_seconds']:.2f} 秒；"
        f"采样中本 Goal 新 simulator 最大并发 {summary['maximum_own_sampled_simulator_concurrency']}。"
        f"最小 cgroup 余量 {summary['minimum_cgroup_headroom_bytes']/2**30:.2f} GiB，"
        f"最小可用磁盘 {summary['minimum_disk_free_bytes']/2**30:.2f} GiB；"
        f"memory/IO full PSI avg10 最大值分别为 {summary['maximum_memory_full_psi_avg10']:.2f} / "
        f"{summary['maximum_io_full_psi_avg10']:.2f}。", '',
        '资源压力与 swap/OOM 计数包含所有项目，不能归因于 DTC；分钟采样不能证明采样间无瞬态。'
        '逐点 time-v 和全局 counter delta 见 [EXECUTION_RESOURCES.tsv](EXECUTION_RESOURCES.tsv) 与 '
        '[RESOURCE_EXECUTION_SUMMARY.json](RESOURCE_EXECUTION_SUMMARY.json)。', '',
        f"期间 host pswpin/pswpout 分别增加 {summary['counters']['pswpin']['last_minus_first']} / "
        f"{summary['counters']['pswpout']['last_minus_first']} pages，"
        f"cgroup swap.current 变化 {summary['counters']['cgroup_swap_current']['last_minus_first']} bytes；"
        f"cgroup oom/oom_kill 增量分别为 {summary['cgroup_events']['oom']['maximum_minus_first']} / "
        f"{summary['cgroup_events']['oom_kill']['maximum_minus_first']}。"
        '不把非零 host swap 活动改写成零，也不从累计历史 oom_kill 推断本次运行发生 OOM。'
        '两个10秒准入 probe 与运行期 emergency 门槛分别核验，见最终资源/身份复核。', '',
        '物理池仍为 640×128B=80KiB，ordinary 16KiB，shared 96KiB，OO PIB128，'
        '4 Tag banks、原有限服务配额与 global lower cap32768 均保持。Tag 从128条增至512条，'
        '逻辑覆盖16KiB→64KiB；每 lookup 最大 way 比较由4增至8。'
        '既有示意 Tag 模型为8864→35840 bits（增加26976 bits，3372 bytes），'
        '只包含既有地址/物理索引/valid/LRU 信息模型；generation、Ref、waiter、布线、端口与时序成本未闭合。'
        '1 cycle lookup 是冻结模拟假设，PPA/native、等面积与同频结论均 UNAVAILABLE。'
        '[RESOURCE_OVERHEAD.tsv](RESOURCE_OVERHEAD.tsv) 的 A/B/T0 行仅是既有审计参考，本轮没有执行这些点。', '',
        '## 身份、预注册与执行收口', '',
        f"完整预注册提交 `{prereg['commit']}` 已于北京时间 "
        f"`{datetime.fromisoformat(prereg['utc']).astimezone(timezone(timedelta(hours=8))).isoformat()}` "
        'push 并 fetch-back，早于两个新启动；'
        f"终态独立复核仍有 {audit['preregistered_files_unchanged']} 份冻结文件逐字节不变。"
        f"实际新启动 {audit['actual_starts']} 次，时间区间最大并发 {audit['maximum_new_DTC_concurrency']}；"
        'DWT2D strict PASS 后才启动 BICG，每个输入一次，没有重试或因性能调整参数。', '',
        f"Framework build `{BUILD_FW}`，Core `{CORE_SHA}`，binary SHA256 `{BINARY_SHA}`。"
        '完整默认值与配置 echo 已逐项核对；相对各自原 OO 只有 sets32→64、ways4→8 两项差异。'
        '12 个原成员及完整 list、10/2 个 ordered kernels、逐 kernel CTA 与 active-thread instructions、'
        '守恒/排空和11项 finite service 的实际验收见 strict/ 与 run_receipts/。', '']
    if terminal['final']['halted']:
        lines += ['原 coordinator 的保守标记 `' + terminal['final']['halted'] + '` 原样保留。'
            '两个授权点都已启动后，独立 EP-L2 更换输出根目录触发旧路径指纹拒绝后续派发。'
            '后续按实际 PID/start_ticks、精确 binary/config/source 身份只读核实为独立项目；'
            '原 coordinator、冻结63文件、timeout 和资源门槛均未修改，BICG 保持原进程运行。'
            '所有采样外部进程身份已闭合；原保守拒绝及首次未知证据不被清除。'
            '详见 [WRAPPER_SCOPE_ASSESSMENT.md](WRAPPER_SCOPE_ASSESSMENT.md)、外部身份收据与最终合同审计。', '']
    lines += ['终态归档曾因第三个新 EP-L2 二进制的13条采样记录中断，原始失败已保存于 diagnostics/。'
        '这13条记录来自两个 PID/start_ticks 身份；恢复后按其精确 fb67448d… binary、'
        'Core/Framework 来源、逐配置及 input metadata SHA 单独闭合，只补充只读身份审计。'
        '197份资源样本中的23个独立外部进程均已识别；没有放宽原执行门槛或增加实际 attempt。'
        '见 [EXTERNAL_PROJECT_UNIFIED_FB_REVIEW.json](EXTERNAL_PROJECT_UNIFIED_FB_REVIEW.json) 与 '
        '[TERMINAL_ARCHIVE_REPAIR_RECEIPT.json](TERMINAL_ARCHIVE_REPAIR_RECEIPT.json)。', '',
        '后台监控只读取终态与心跳，不负责 simulator 启动、重试或科学验收。'
        '终态归档工具也只在原执行权与 simulator 退出后读取完整 raw。'
        'strict、原始终态文件 SHA、输入/source/config 身份与独立数值重算见 '
        '[STRICT_AUDIT.json](STRICT_AUDIT.json)、[FINAL_CONTRACT_AUDIT.json](FINAL_CONTRACT_AUDIT.json)、'
        '[RAW_FILES_SHA256.tsv](RAW_FILES_SHA256.tsv) 和最终 FILES_SHA256.tsv。', '',
        '## 科学边界与交审范围', '',
        '原 GEMM/Gaussian 的 A/B/C 全矩阵只作已完成发现证据，不参与本轮新选型。'
        '本轮所有正负收益或失败均保留，不增加性能阈值。'
        '没有独立 sector 返回、内部 MSHR 占用和数值 load 正确性的输出证明，这些项目保持 UNAVAILABLE。', '',
        'Lane A/M/T、原44行（41 PASS、3旧 Hotspot HOLD）、原 raw/control/locks、'
        'GM12 未定义状态、modern128 HOLD 和 v0.11-VI 主图均保持。'
        '本轮不授予 T1-C 论文主配置替换权，不开启 T2、新协议/机制/模型、物理池调参、新 Tag 或第三输入。'
        '完整声明见 [SCIENTIFIC_SCOPE.md](SCIENTIFIC_SCOPE.md)。', '',
        '大 raw 保留 `/workspace/dtc-t1c-holdout-174-v1`；Git 仅提交小型审查证据。'
        '最终 HEAD/tree、全部文件 SHA、远端 fetch-back 与 clean 状态由独立 raw root 中的最终发布收据闭合，避免自引用哈希。', '']
    (PACK / 'LATEST_REPORT.md').write_text('\n'.join(lines))
    print('Rendered complete terminal scientific review report')


if __name__ == '__main__':
    main()
