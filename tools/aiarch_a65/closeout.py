"""Archive actual outcomes only; preserve original disk STOP and all new legal evidence."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from paths import R, ROOT, OLD, W, CLEANUP, save, sha, allocated

O = W / 'docs/ai_workload_research/runs/AI_ARCH_A65_IGB_SMALL_COMPILED_NUMERIC_109_V1'


def load(name, default=None):
    p = R / name
    return json.loads(p.read_text()) if p.exists() else default


def link_copy(source, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert sha(source) == sha(dest)
    else:
        os.link(source, dest)


def compact_copy(source, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = source.read_bytes()
    with dest.open('wb') as f:
        with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0) as z:
            z.write(body)
    assert gzip.decompress(dest.read_bytes()) == body


def main():
    clean = json.loads((CLEANUP / 'finished.json').read_text())
    assert clean['status'] == 'PASS_FIRST_BATCH_CLEANUP'
    ledger = load('gpu_ledger.json')
    assert ledger and ledger['cumulative_seconds'] <= 180
    assert load('post_readonly_audit.json')['status'] == 'PASS'
    numeric = load('numeric_result.json')
    updates = load('update_ledger.json', {'reserved': 0, 'completed': 0})
    status = numeric['scientific_status'] if numeric else 'NUMERIC_INSTRUMENTATION_INCOMPLETE'
    if numeric is None and ledger['attempts'][-1]['reason'] == 'GPU_LOCK_DEFERRED':
        status = 'GPU_LOCK_DEFERRED'
    # Original published STOP remains addressable at fbb0fe21 and byte-identical here.
    history = O / 'history/initial_cpu_disk_stop'
    history.mkdir(parents=True, exist_ok=True)
    for name in ['FINAL_REPORT.md', 'GATES.json', 'RESOURCE_RECEIPT.json', 'ASSET_PRESENCE_ONLY.json', 'AUTHORITY_IDENTITY.json', 'LOCK_RECEIPT.json', 'READONLY_CHECK.json', 'RESOURCE_STOP.json', 'STATIC_REVIEW.json', 'PUBLISH_CPU_OBSERVATION.json', 'raw/df_cpu_admission.txt', 'raw/remote_start_HEAD.txt', 'SHA256SUMS']:
        body = subprocess.check_output(['git', 'show', 'fbb0fe210903872ace1005456b3fd8374d38abee:' + str((O / name).relative_to(W))], cwd=W)
        (history / name).parent.mkdir(parents=True, exist_ok=True)
        (history / name).write_bytes(body)
        if name not in ['FINAL_REPORT.md', 'GATES.json', 'RESOURCE_RECEIPT.json', 'SHA256SUMS']:
            if (O / name).exists():
                (O / name).unlink()
    for p in R.glob('*.json'):
        if p.name == 'old_A61_metadata_before.json':
            continue
        link_copy(p, O / 'raw' / p.name)
    for p in R.glob('*.log'):
        link_copy(p, O / 'raw' / p.name)
    for p in R.glob('raw/*.npz'):
        link_copy(p, O / 'raw' / p.name)
    for p in R.glob('attempt_sources/*/*.py'):
        link_copy(p, O / 'raw/attempt_sources' / p.parent.name / p.name)
    if (R / 'events.jsonl').exists():
        link_copy(R / 'events.jsonl', O / 'raw/events.jsonl')
    cache = []
    for root in [R / 'cache', R / 'tmp']:
        for p in root.rglob('*'):
            if p.is_file() and not p.is_symlink():
                cache.append({'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)})
    (O / 'COMPILER_CACHE_MANIFEST.json').write_text(json.dumps({'private_files': cache,
        'bytes': sum(x['bytes'] for x in cache), 'no_cache_binary_redistributed': True}, indent=2) + '\n')
    dest = O / 'storage_cleanup'
    dest.mkdir(exist_ok=True)
    for p in CLEANUP.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(CLEANUP)
        if p.suffix in ['.json', '.jsonl'] and p.stat().st_size > 128 * 1024:
            compact_copy(p, dest / (str(rel) + '.gz'))
        else:
            link_copy(p, dest / rel)
    source = ROOT / 'preflight_resume.log'
    if source.exists():
        link_copy(source, O / 'raw/preflight_resume.log')
    for p in ROOT.glob('library_audit_pre*.log'):
        link_copy(p, O / 'raw' / p.name)
    phases = {'scientific_status': status, 'initial_disk_STOP': 'PRESERVED_IN_HISTORY_AND_ORIGINAL_COMMIT',
              'cleanup': clean['status'], 'G0_CPU_source_asset_library_and_comparator': 'PASS',
              'G1_triplet_observations': 'COMPLETE' if numeric else 'INCOMPLETE',
              'G1_same_batch_numeric_alignment': 'PASS' if status == 'SAME_BATCH_NUMERIC_CONTROL_PASS' else 'NOT_QUALIFIED',
              'GPU_terminal_supervisor_flag': ledger['attempts'][-1]['reason'],
              'full_exclusivity_qualification': 'UNRESOLVED_TERMINAL_NVML_PID_FLAG',
              'readonly_post_audit': 'PASS', 'formal_training': 'NOT_RUN_NOT_AUTHORIZED',
              'automatic_next_GPU_task': False}
    (O / 'GATES.json').write_text(json.dumps(phases, indent=2) + '\n')
    attempts = ledger['attempts']
    resources = {'GPU_lock_cumulative_seconds': ledger['cumulative_seconds'],
                 'peak_sampled_tree_RSS_bytes': max(x['peak_sampled_tree_RSS_bytes'] for x in attempts),
                 'peak_sampled_GPU_MiB': max(x['peak_sampled_GPU_MiB'] for x in attempts),
                 'qualification_calls_reserved': updates['reserved'],
                 'completed_qualification_observations': updates['completed'],
                 'formal_updates': 0, 'downloads': 0, 'dependency_installs': 0,
                 'allocator_fraction': .70, 'CPU_affinity': [0, 2, 4, 6],
                 'new_disk_unique_allocated_including_cleanup_bytes': allocated(),
                 'source_control_extra_allocation_estimate_bytes': 0,
                 'FS_free_after_cleanup_bytes': clean['free_after_bytes'],
                 'FS_free_current_bytes': shutil.disk_usage(R).free,
                 'sampling_limit': 'RSS/NVML sampled, transient peaks may be missed; .70 allocator and early margins retained',
                 'Torch_peak_allocated_bytes': numeric.get('Torch_peak_allocated_bytes') if numeric else None,
                 'Torch_peak_reserved_bytes': numeric.get('Torch_peak_reserved_bytes') if numeric else None,
                 'all_owned_GPU_children_ended': all(x['all_owned_processes_ended'] for x in attempts),
                 'prior_CPU_only_STOP_GPU_seconds': 0,
                 'terminal_supervisor_reason': attempts[-1]['reason'],
                 'full_exclusivity_qualification': 'UNRESOLVED_TERMINAL_NVML_PID_FLAG'}
    if numeric:
        resources['actual_qualification_updates'] = numeric['actual_qualification_updates']
    (O / 'RESOURCE_RECEIPT.json').write_text(json.dumps(resources, indent=2) + '\n')
    comparison = load('parameter_comparisons.json', {})
    lines = ['# A65：同 batch 编译更新数值诊断与首批存储清理', '',
             '**科学终态：' + status + '。** 本轮在用户批准首批清理并继续 A65 后执行。', '',
             '执行分支 `hrl/aiarch-a65-igb-small-compiled-numeric-109-v1`，原固定 Goal 起点 `afe42345c4b0c45b3e09f3cb32ce4e3e0de09989`。初次磁盘 STOP 及发布收据保持在 `history/initial_cpu_disk_stop` 与原提交 `fbb0fe210903872ace1005456b3fd8374d38abee`。没有 merge 协调分支或修改原 A61 STOP。', '',
             '## 首批清理', '',
             '仅删除用户批准的两处 pip HTTP cache、五份固定 revision incoming 模型副本，以及 E1 v3 两处闭合硬链接 trace；保留其余模型、控制文件、manifest/ACK、A61/A26GR1、NequIP 和 164 权威归档。', '',
             f"164 当前全量 SHA256 核验 **{clean['remote_verified_files']} 项**，109 本地 SHA 核验 **{clean['local_verified_payload_files']} 项**；模型与 trace 两端都与固定归档清单一致后才删除。E1 的 9,032 个 raw 文件各有两条硬链接，成对解除后只计一次实际空间。", '',
             f"文件系统可用量从 {clean['free_before_bytes']} bytes 升至 {clean['free_after_bytes']} bytes（{clean['free_after_bytes']/1024**3:.3f} GiB）。df 净变化含同时发生的外部文件系统活动；逐目标的 allocated/file 数、前后 df 和完整 SHA 记录在 storage_cleanup。", '',
             '清理工程记录：初次占用检查将不可读 SSH/PAM 基础进程混同未知工作进程，修正后重验；首次归档 SHA 因 SSH 断线中断，改为 174-new 自有 /tmp 持久化逐文件记录、两个受限只读 SHA workers，完成后回读。最终汇总曾把110+9062误写为9182；全部逐文件SHA已通过后，按实际清单集合重新核对为9172并修正计数，复用mtime/size不变的持久化校验结果，未重新读取大payload。所有失败记录保留。没有写164归档或删除未验证payload。', '',
             '## 输入、环境和独立性', '',
             '只读复用 A61 已接受的官方 IGB-small：1,000,000×1024 FP32 features、19 类、原 20261015 split、有向 CSC 13,070,502 edges。官方 tar SHA256 `fa237780a84b7d1956c180564a9d080d61b43b32b2bf2810b3960f1ab028a919`，feature/edge/CSC/split/order 全部重新核 SHA。', '',
             'Torch 2.2.0+cu121 / DGL 2.4.0+cu121 / PyG 2.6.1 / NumPy 1.26.4 / Triton 2.2.0 保持。新 runtime 仅用 symlink 建立同包只读视图，无安装或下载；排除旧 sitecustomize，使用只允许 A65 输出的独立写保护与 cache 路径。未 import 或执行旧 common.py、gpu_supervisor.py、native.py。', '',
             '原 GraphSAGE、train_step、DataContext 与 validate_mb 按 AST 完全复制审计：3 层 mean、hidden256、fanout10/10/10、B1024、FP32 highest、TF32 关闭，Adam lr.003、weight_decay0、默认 betas/eps1e-8；编译入口仍是 torch.compile(train_step,dynamic=True)。', '',
             '运行前后核 10,686 项核心运行库 SHA/size/mtime、A61 owned package RECORD、39 份原缓存 wheel；一份 NumPy 自带 pyc 因 pip 重新编译与 wheel RECORD 不同，已经同版本 Python 逐代码对象验证与同 SHA 源码一致。没有重写 bytecode、源码或二进制。CPU 比较器 12 项定向检查通过。', '',
             '## 实际数值观察', '']
    if numeric:
        frozen = load('frozen_input_identity.json')
        lines += [f"仅一份新自然 B1024 batch，采得 **{frozen['input_nodes']}** 个输入节点。PINNED_CACHE_ON feature128MiB、graph1,000,000edges、async/pinned overlap 原路径，未作 cache replay 或再采邻域。实际 subgraph/IDs/labels 保留 NPZ；完整 fetched FP32 features 与只读源逐字节比较后冻结，每路执行前后完整输入 SHA 相同。", '',
                  '从唯一 seed20261015 CPU 初态建立三份独立模型和初始空 Adam state；完整 name/count/order/shape/dtype/逐参数 SHA 和 storage 身份分开记录。三路初态 bitwise 相同，无 parameter 或 optimizer buffer 跨模型共享。', '',
                  '| 路径 | 实际资格更新 | loss |', '|---|---:|---:|']
        for tag, value in numeric['all_losses'].items():
            lines.append(f'| {tag} | 1 | {value:.12g} |')
        lines += ['', '每路均为原 train_step 的 forward/crossentropy/backward/Adam 真更新。所有 initial/gradient/updated 张量与逐参数统计保留 raw；没有正式训练窗口或 profiler。更新门严格使用实际 Torch allclose(A,B,atol1e-6,rtol1e-4)，名称门单独判断；loss 门1e-5/1e-4。maxrel 的1e-12诊断分母不改变门限；完整 batch paired gradient 的旧1e-5/1e-3数值仅作描述，未冒充旧16seed FP64 oracle 资格。', '',
                  '| 参数 | A/B 失败元素 | A/C 失败元素 | A/C maxabs | A/C maxabs/tol |', '|---|---:|---:|---:|---:|']
        ab = comparison['updated_parameter_eagerA_eagerB']['parameters']
        ac = comparison['updated_parameter_eagerA_compiledC']['parameters']
        for name, row in ac.items():
            lines.append(f"| {name} | {ab[name]['failed_elements']} | {row['failed_elements']} | {row['max_abs']:.8g} | {row['max_abs_over_tolerance']:.6g} |")
        lines += ['', 'first_failures、对应初值/gradient/更新量、所有参数的 gradient 和 signed update-delta 比较，以及同 gradient 的首步 Adam CPU 解析式核验见 parameter_comparisons.json / failure_element_attribution.json。cold compile wall 和 Dynamo graph breaks 仅为资格 metadata，不是性能样本。', '']
    else:
        lines += ['GPU 子进程没有形成完整 triplet；已完成部分和原始错误按记录保留，未运行项不补造。详见 gpu_ledger / runner_failure / update_ledger。', '']
    lines += ['## 数值定位和监督边界', '',
              'A/B 所有参数在原更新门通过；A/C 只有 layers.0.lin_r.weight[59,378] 一个元素失败。原参数值0.0034851767122745514，eagerA梯度3.1561739888275042e-9、compiledC梯度3.1678837331128307e-9，相差约1.171e-11；更新后分别0.0027654748409986496 / 0.0027634433936327696，差2.0314473658800125e-6，允许量约1.276344339363277e-6。三路均满足各自同梯度的原首步Adam CPU解析式；证据支持先有微小梯度差异、经eps1e-8附近的Adam敏感性放大，不能据此声明不同optimizer语义或Torch bug。', '',
              '监督器末次轮询保留 EXTERNAL_GPU_TASK_STOP 标志：此时阶段已为 NUMERIC_OBSERVATIONS_COMPLETE_STOP、子进程退出码0，最终NVML列表为空，但触发标志时的PID列表未保存。源码CPU定向复现证明“先读NVML、再读已退出进程组”可能误报自身退出；本次具体PID未捕获，不能将可能性改写为已证明的误报，也不声称完整独占资格PASS。原始flag保持，未改已执行GPU源码，未为此追加GPU重试。见 terminal_supervisor_guard_audit.json。该监督缺口与已实际记录的1元素数值超门分别报告。', '',
              '## 资源与范围', '',
              f"GPU 共享锁非阻塞，累计 **{ledger['cumulative_seconds']:.6f}s / 180s**；采样树 RSS峰 **{resources['peak_sampled_tree_RSS_bytes']/1024**3:.3f}GiB**，NVML 进程显存峰 **{resources['peak_sampled_GPU_MiB']}MiB**。原 allocator fraction .70 与提前退出余量保留；采样可能漏瞬时峰，另保留 Torch allocator 峰值。所有自有子进程结束后释放锁。", '',
              f"资格观察完成 {updates['completed']}，正式训练 **0**，下载/安装 **0**。新增磁盘按 inode 去重计量，报告、raw、cache、worktree 与本次清理记录纳入保守账；最终 Git 对象增量与 128MiB 门在发布前再次核算。CPU affinity 0,2,4,6，OMP≤4、Torch4、DataLoader0。", '',
              '原 A61 源码/raw/cache/数据/环境全目录 metadata 前后一致，核心 DLL 与输入 payload SHA 回读不变。旧 A61 已有的失败不被本次新 batch 的结果追溯改写。A65 初次发布 Git pack 最大线程数未测的历史缺口仍保存在 history/initial_cpu_disk_stop/PUBLISH_CPU_OBSERVATION.json；本次后续命令均受四核 affinity 和逐命令 pack/index threads=4 限制。', '',
              '## 科学解释与停止', '',
              '本轮仅判断新受控 batch 的数值资格；不证明旧失败根因、Torch bug、正式训练性能、供数瓶颈或硬件收益。无论三路一致还是不一致，都保持原门限并在本轮归档后 STOP。若 eager/eager 自身超门，先接受自然数值波动证据；若仅 compiled 超门，记录编译路径不对齐并逐阶段分析，不自动归罪编译器。后续 GPU 科研须独立审查，本次不会自动启动 A61。', '',
              'Contains information from Illinois Graph Benchmark (IGB), Khatua et al., KDD2023，按原已接受 ODC Attribution License1.0 的本地数值科研范围使用。原始特征、完整图、环境和编译二进制不入 Git；仅发布本 Goal 授权的小型受控子图/IDs、模型与 gradient 观察、代码和证据。', '',
              '仅发布本独立分支。commit/tree/全部新增 blob/SHA 远端 fetch-back 与工作区 clean 收据在最终回执及独立私有 final_git_readback.json 保存，避免 commit 自引用。STOP。', '']
    (O / 'FINAL_REPORT.md').write_text('\n'.join(lines))
    # Include conservative new Git blob allocations without counting shared old objects.
    changed = [p for p in O.rglob('*') if p.is_file()] + [p for p in (W / 'tools/aiarch_a65').iterdir() if p.is_file()]
    object_bound = sum(((p.stat().st_size + 4095) // 4096) * 4096 for p in changed) + 1024**2
    resources['source_control_extra_allocation_estimate_bytes'] = object_bound
    resources['new_disk_conservative_final_bound_bytes'] = allocated() + object_bound
    assert resources['new_disk_conservative_final_bound_bytes'] < 128 * 1024**2, 'FINAL_NEW_DISK_BUDGET_STOP'
    (O / 'RESOURCE_RECEIPT.json').write_text(json.dumps(resources, indent=2) + '\n')
    all_files = sorted([p for p in O.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'] +
                       [p for p in (W / 'tools/aiarch_a65').rglob('*') if p.is_file()])
    (O / 'SHA256SUMS').write_text(''.join(sha(p) + '  ' + str(p.relative_to(W)) + '\n' for p in all_files))
    save('execution_terminal.json', {'scientific_status': status, 'stop': True, 'future_GPU_task': False})
    print('ARCHIVE_PREPARED', status, len(all_files), resources['new_disk_conservative_final_bound_bytes'], flush=True)


if __name__ == '__main__':
    main()
