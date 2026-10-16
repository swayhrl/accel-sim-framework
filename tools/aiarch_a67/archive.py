"""A67 publication from immutable observed data; no GPU APIs or new training."""
import gzip,json,os,shutil,subprocess,statistics
from pathlib import Path
from paths import R,W,OLD,OLD65,sha,save,allocated,usage,new_raw_allocated
O=W/'docs/ai_workload_research/runs/AI_ARCH_A67_IGB_SMALL_EAGER_SCOPE_BOUNDED_WALL_109_V1'

def link(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert sha(src)==sha(dst)
 else:os.link(src,dst)

def compact(src,dst):
 body=src.read_bytes();dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('wb') as f:
  with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(body)
 assert gzip.decompress(dst.read_bytes())==body

def main():
 a=json.loads((R/'analysis.json').read_text());g=json.loads((R/'gpu_ledger.json').read_text());num=json.loads((R/'G1_OFF_numeric.json').read_text());post=json.loads((R/'post_readonly_audit.json').read_text())
 assert post['status']=='PASS' and g['reason'] is None and g['exclusivity_evidence_complete']
 O.mkdir(parents=True,exist_ok=True)
 for p in R.glob('*.json'):
  if p.name.startswith('old_A'):
   compact(p,O/'raw'/(p.name+'.gz'))
  else:link(p,O/'raw'/p.name)
 for p in R.glob('*.jsonl'):link(p,O/'raw'/p.name)
 for p in R.glob('*.log'):link(p,O/'raw'/p.name)
 for p in (R/'raw').rglob('*'):
  if p.is_file():link(p,O/'raw'/p.relative_to(R/'raw'))
 for p in (R/'executed_sources').glob('*.py'):link(p,O/'raw/executed_sources'/p.name)
 for source,name in [('/tmp/aiarch_a67_cpu_preflight.log','cpu_preflight.log'),('/tmp/aiarch_a67_library_pre.log','library_pre.log')]:
  link(Path(source),O/'raw'/name)
 for commit,path,name in [('759dc19022233b375af626761f058c2eb898350b','docs/ai_workload_research/reviews/AI_ARCH_A66_A65_SAME_BATCH_NUMERIC_AND_STORAGE_INDEPENDENT_REVIEW_2026-10-16_V1.md','A66_READONLY.md'),('326dcac6227d1c1af6b38e4f76d21566525f35aa','docs/ai_workload_research/reviews/AI_ARCH_A64_A61_GNN_NUMERIC_STOP_INDEPENDENT_REVIEW_2026-10-16_V1.md','A64_READONLY.md')]:
  target=O/'authority'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(subprocess.check_output(['git','show',commit+':'+path]))
 source=W/'docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1/GRAPH_AND_TRAIN_IDENTITY.json';shutil.copyfile(source,O/'INPUT_AND_TRAIN_IDENTITY.json')
 diffs={}
 for old,new,name in [('tools/aiarch_a61/native.py','tools/aiarch_a67/native.py','runner.diff'),('tools/aiarch_a65/gpu_supervisor.py','tools/aiarch_a67/gpu_supervisor.py','supervisor.diff')]:
  result=subprocess.run(['diff','-u',str(W/old),str(W/new)],capture_output=True);assert result.returncode in [0,1];target=O/'source_diffs'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(result.stdout);diffs[name]={'reference':old,'A67':new,'diff_SHA256':sha(target)}
 (O/'SOURCE_DIFF_IDENTITY.json').write_text(json.dumps(diffs,indent=2)+'\n')
 gates={'scientific_status':a['scientific_status'],'scope':'EAGER_ONLY','G0':'PASS_FROZEN_AUTHORITY_PAYLOAD_ABI_RECORD_SOURCE_SUPERVISOR_TESTS_RESOURCES','G1_OFF':'PASS_NEW_1_UPDATE_FP64_SMALL_ORACLE_AND_FP32_ADAM','G1_FULL':'PASS_NEW_WARMUP_AND_ACTUAL_FULL_RESIDENT_CAPACITY','G1_ON':'PASS_NEW_INPUT_FINITE_NONZERO_CACHES_AND_ACCEPTED_HISTORICAL_ORACLE','G2':'PASS_6_WINDOWS_72_FORMAL_12_WARMUP','G3':'METADATA_ONLY_NO_NEW_GPU_DIAGNOSTIC_OR_UPDATES','supervision':'PASS_CAPTURED_PIDS_BIRTHS_WINDOW_BOUNDARIES_AND_FINAL_EMPTY','post_readonly':'PASS_A61_A65_CORE_RUNTIME_AND_INPUTS_UNCHANGED','compiled_path':'NOT_RUN_OLD_A65_FAIL_PRESERVED','CONVERGENCE_NOT_EVALUATED':True,'no_next_GPU_task':True}
 (O/'GATES.json').write_text(json.dumps(gates,indent=2)+'\n')
 resources={'GPU_lock_cumulative_seconds':g['cumulative_lock_seconds'],'peak_sampled_task_RSS_bytes':g['peak_sampled_RSS_bytes'],'peak_sampled_GPU_MiB':g['peak_sampled_GPU_MiB'],'CPU_affinity':[0,2,4,6],'Torch_threads':4,'DataLoader_workers':0,'downloads_installs_bytes':0,'formal_updates':72,'warmup_updates':12,'qualification_updates':1,'total_actual_updates':85,'training_retries':0,'initial_CPU_prepare_seconds':json.loads((R/'G0_final.json').read_text())['CPU_prepare_seconds'],'new_raw_and_logs_unique_allocated_bytes':new_raw_allocated(),'new_disk_unique_allocated_before_Git_bytes':allocated(),'FS_free_bytes':shutil.disk_usage(R).free,'all_owned_GPU_processes_ended':g['all_owned_processes_ended'],'shared_lock_released':g['shared_lock_released'],'NVML_final_empty':g['final_NVML_empty'],'sampling_limit':g['sampling_limit'],'historical_authority_files_inherited_in_worktree_counted_in_disk_not_new_raw':True}
 pin=json.loads((R/'pinned_preparation.json').read_text())
 timing={'common_pin_once':pin,'per_window':[{'arm':x['arm'],'seed':x['seed'],'ctx_preparation_seconds':x['ctx_preparation_seconds'],'warmup_seconds_including_audits':x['warmup_with_audits_seconds'],'formal_wall_seconds':x['wall_seconds']} for x in a['windows']],'cold_init_evidence':'GPU_child_launch,device_and_software,events and PID/proc/NVML timestamps; no cold/startup number used as throughput denominator','boundary_ack':'outside formal timer, not free system E2E work','formal_scope':'steady-state 12 natural complete training updates, starts before formal iterator; no perstep synchronization/loss scalar readback','not_measured':'single-step latency distribution, physical PCIe/DRAM bytes or synchronized supply waits'}
 (O/'PREPARATION_AND_TIMING_SCOPE.json').write_text(json.dumps(timing,indent=2)+'\n')
 lines=['# A67：IGB-small eager-scope 三路径完整训练步 Discovery','',
 '**科学终态：SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE。** 两个冻结seed上，完整GPU驻留均快于PINNED_CACHE_ON/OFF；本固定128MiB feature cache＋1M-edge graph cache配置的ON还慢于OFF。结果支持当前IGB-small/RTX4080 eager范围存在可用且更快的成熟全驻留软件替代，不支持从ON/OFF差异直接推进新硬件。','',
 '用户明确批准A67的新eager科学范围及有界预算，覆盖Goal历史待派发状态。本轮不是恢复A61、重试A65 compiled C或调整其数值阈值。执行分支 `hrl/aiarch-a67-igb-small-eager-scope-wall-109-v1`，固定起点 `266314db14686b75d643c446824ebf8d59ba3a51`；A61 `37120f98186b83a946f4812755523f5d73245491`、A65 `3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79` 的数据、环境、源码、报告与STOP保持只读。','',
 '## 数值、输入与执行门','',
 'G0 PASS：官方IGB-small tar、原1024 FP32 feature/19类标签/有向自环CSC13,070,502 edges、20261015 split和两seed原node-order前缀完整SHA核验；Torch2.2.0+cu121/DGL2.4.0+cu121/PyG2.6.1/NumPy1.26.4/Triton2.2.0与原权威相同。原包仅以新runtime symlink视图只读复用，所有cache/tmp和写保护均归A67，无依赖安装、数据下载或旧cache清理。完整阅读A61/A65报告与源码、A64和A66审查，固定审查提交及blob/SHA见authority_identity。','',
 'GraphSAGE/train_step/DataContext/model_optimizer/numeric_oracle/state_hash等算法定义与A61源AST一致，差分只改变隔离包装、固定窗口编排、预算与监督。3层mean/hidden256、fanout10/10/10、B1024、FP32 highest/TF32禁止、crossentropy和Adam lr.003/weight_decay0/defaultbetas/eps1e-8均不改；没有调用torch.compile。','',
 f"G1 OFF新自然B1024数值PASS：16seed的CPU FP64仅作数学oracle，训练仍FP32。最大forward差 {num['forward_max_abs_error']:.9g}，参数gradient差 {num['max_parameter_gradient_abs_error']:.9g}，首步Adam差 {num['max_Adam_first_update_abs_error']:.9g}，严格使用原门。仅这一次额外资格更新；FULL/ON不重复旧canary训练，以各自2次自然warmup做本轮真实输入、缓存/驻留、梯度/权重finite与容量门。",'',
 '所有6窗口PASS：每格2次warmup接12次正式更新，逐参数Adam step=14；OFF独立canary step=1。合计1资格＋12warmup＋72formal=85次实际更新，没有重跑窗口或额外训练。每种seed在三arm的初态模型SHA及实际formal seed-node-order SHA一致；异步邻域不保证逐边一致，不能称bitwise逐样本因果配对。warmup两批与正式最后一批做全采样边membership/fanout及256行真实特征/标签审计，正式中段保留全部采样计数并使用相同已审GraphBolt路径；不宣称独立复核了每一批的每条边。','',
 '## 六个原始正式窗口','',
 '| 顺序 | seed | arm | 更新 | 完整wall(s) | 平均batch(ms) | seed nodes/s |','|---:|---:|---|---:|---:|---:|---:|']
 for x in a['windows']:lines.append(f"| {x['position']} | {x['seed']} | {x['arm']} | 12 | {x['wall_seconds']:.9f} | {x['mean_complete_batch_ms']:.6f} | {x['natural_seed_nodes_per_second']:.3f} |")
 lines += ['', '每个wall都从创建正式iterator之前开始，覆盖sampling→feature-ready→forward/backward→Adam，最后一次GPU同步完成才停表；中途无每step同步、loss.item、NVTX、NCU/NSYS/NVBit。逐批仅记录已有张量shape/采样计数和保留很小的seed-ID张量，全部hash/CPU读回、finite验证及loss数值提取都在停表后。完整12个loss及实际sampling计数、初态/前后参数SHA、缓存计数、Torch峰和父监督per-run RSS/NVML峰均在raw及analysis.json。平均batch由window/12推导，没有伪造12个独立latency样本。','',
 f"公共pin准备实测 {pin['seconds']:.6f}s；FULL每格上传全量4,096,000,000B FP32 feature和完整CSC，ctx准备约0.218s。各格实际准备/带审计warmup另列PREPARATION_AND_TIMING_SCOPE.json。冷启动有child launch/阶段/PID时间线，未把GPU持锁或准备成本当train latency，也不把预上传当免费系统端到端加速。",'',
 '## 效果、缓存和界限','']
 for x in a['per_seed_ratios']:lines.append(f"- seed{x['seed']}：ON/FULL wall={x['ON_wall_over_FULL']:.4f}；OFF/FULL={x['OFF_wall_over_FULL']:.4f}；ON/OFF={x['ON_wall_over_OFF']:.4f}。")
 lines += ['', '两个seed方向一致，但FULL窗口0.311s与0.435s差异较大，短窗口及顺序/采样离散限制明显；这些是本次实际比值，不是精确可泛化速度比或显著性置信区间。每arm只有2个独立窗口，12个batch不能冒充12次独立计时重复。','',
 'ON缓存确实生效：feature容量134,217,728B，graph cache请求1,000,000edges；两seed在warmup＋formal之后feature cumulative miss约95.44–95.46%，graph cumulative miss约87.82%，且存在真实命中。OFF两cache均关闭，FULL完整原图/原FP32 feature在GPU。低命中及维护路径可能解释本配置ON较慢，但本轮未分解CPU、PCIe、GPU memory或同步等待，命中率不等于性能因果比例、logical feature bytes不等于实际PCIe/DRAM流量。','',
 'G3仅使用已有计数、输入信息和已保存wall做CPU分析，没有额外同步诊断或GPU更新。FULL在12GiB预算下完成自然连续训练且更快，支持SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE；并非排除所有后端，compiled资格仍FAIL。没有最终accuracy/全epoch收敛或新硬件headroom结论。','',
 '## PID监督与资源','',
 f"A65退出边界缺口在新A67 supervisor中修正：known child PID/start_ticks/PGID/SID跨退出保留，采样同时保存NVML原CSV、查询起止、前后/proc身份与child终态；未知PID即便同PGID也STOP，PID复用或无法证明归属也STOP。CPU10项归属＋6项解析测试通过。每窗口计时外等待父监督边界快照。实际保留 {a['PID_snapshots']} 次NVML快照，classification只有OWN_LIVE_PID或空，未遇到真实第三方或无法归属PID；本次没有宣称设备上重现了旧A65末次竞态，旧A65未被重标PASS。",'',
 f"GPU锁非阻塞累计 {g['cumulative_lock_seconds']:.6f}s /900s，采样RSS峰 {g['peak_sampled_RSS_bytes']/1024**3:.6f}GiB，NVML峰 {g['peak_sampled_GPU_MiB']}MiB；CPU affinity0,2,4,6、Torch4、DataLoader0，保留allocator .70。瞬时峰可能漏采，另有各窗口Torch allocator精确峰和资源提前余量。所有自有GPU子进程结束、最终NVML空后释放原锁。",'',
 '原输入与10,686项核心运行库SHA/size/mtime、9,701项A61-owned RECORD及39份缓存wheel前后核验，NumPy既有pyc重编译差异沿用同版本源码code-object证明；A61/A65目录metadata前后一致。没有新删除、164访问、驱动/核心包升级或旧任务恢复。256MiB新增盘和32MiB新raw/log均按实际inode去重及保守Git对象账核算，CPU准备低于1小时。','',
 '## NEXT_MINIMAL_RECOMMENDATION 与STOP','',
 '仅建议CPU-only独立审查本精确commit的六窗口原始证据、FULL容量与准备成本范围、cache与PID边界，再收口当前IGB-small eager硬件供数假说。建议预算CPU≤2、RAM≤512MiB、新盘≤16MiB，GPU/下载/安装0；身份、计时边界或PID/raw不一致即STOP。没有新的GPU或更大图授权，不在本轮继续调cache容量、编译器、profiler或硬件机制。','',
 'Contains information from Illinois Graph Benchmark (IGB), Khatua et al., KDD2023，按原已接受ODC Attribution License1.0本地数值科研范围使用；不重新分发完整feature、图、原archive或venv。源代码Apache2归属保留。','',
 '仅push本A67执行分支，不merge协调分支。原Goal、实际执行source、差分、全部合法raw/负发现/资源和SHA归档。最终commit/tree/blob/SHA fetch-back与worktree clean收据独立保存以免自引用；发布后STOP，不自动开启下一GPU任务。','']
 (O/'FINAL_REPORT.md').write_text('\n'.join(lines))
 # Count conservative prospective Git blobs as well as real output/worktree allocations.
 candidates=[p for p in O.rglob('*') if p.is_file()]+[p for p in (W/'tools/aiarch_a67').rglob('*') if p.is_file()]
 git_bound=sum(((p.stat().st_size+4095)//4096)*4096 for p in candidates)+1024**2
 resources.update(new_raw_and_logs_unique_allocated_bytes=new_raw_allocated(),new_disk_unique_allocated_before_Git_bytes=allocated(),prospective_Git_blob_allocated_bound_bytes=git_bound,new_disk_conservative_final_bound_bytes=allocated()+git_bound)
 assert resources['new_raw_and_logs_unique_allocated_bytes']<32*1024**2
 assert resources['new_disk_conservative_final_bound_bytes']<256*1024**2
 (O/'RESOURCE_RECEIPT.json').write_text(json.dumps(resources,indent=2)+'\n')
 files=sorted([p for p in O.rglob('*') if p.is_file() and p!=O/'SHA256SUMS']+[p for p in (W/'tools/aiarch_a67').rglob('*') if p.is_file()])
 (O/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(W))+'\n' for p in files))
 save('execution_terminal.json',{'scientific_status':a['scientific_status'],'STOP':True,'no_next_GPU_task':True})
 print('A67_ARCHIVE_READY',len(files),'NEW_DISK_BOUND',resources['new_disk_conservative_final_bound_bytes'],'RAW',resources['new_raw_and_logs_unique_allocated_bytes'],flush=True)

if __name__=='__main__':main()
