# R0.1一次静态复核

Core保持62dc1d179b5516e68b21b695c7a9c5d0667e9671；tree23f407cfadc7728b50f6f91177319ada4029cd2b等于Core发布c93d900e。没有新的Core改动、编译或模拟。Framework53a1503d只修构建工具与工具测试；相对原候选34b32a01，gpu-simulator路径无差分。原r3的source/patch静态检查保留引用，不重跑或升级为runtime PASS。

| 门槛 | 源码实际路径和断言 | 覆盖/局限 | 本次结果 |
|---|---|---|---|
| physical_bank_clock | `test_ft_memcpy_clock.cc`驱动真实memory partition→L2interface→lower→set_done，每个物理周期观察4个bank grant增量 | B/U × C8/16 × offset0/4096，加非零offset warm-hit；WBUF/WAD压力、不同释放寿命及终态。版本0 warm回复；任何bank delta>1返回42 | 静态已读；12条计划，NOT_COMPILED_NOT_RUN |
| memcpy_payload_identity | `test_ft_host_prefill.cc`的test_gpu经实际`perf_memcpy_to_gpu`使用真实GPU分区；配置1slice/1Tag用于受控冲突 | 64位地址、非对齐端点、零长度、重复/部分sector、handle/generation/原生选择index、clean eviction/miss/fill、版本0真正warm read、无lower read | 静态已读；4条计划，NOT_COMPILED_NOT_RUN |
| dirty/active拒绝与WB | 同host测试，GPU write的uid+1版本，try接口拒绝前后不变；子进程实际void入口必须SIGABRT | dirty同地址/被驱逐行、WAD待完成、frontend pending、被背压ICNT回复拒绝；普通GPU驱逐产生真实versioned WB并完成set_done后再预热；core dump限额0 | 与host测试同4条；无新增runtime证据 |
| 受影响WB回归 | `test_ft_partition.cc`和`test_ft_wbuf.cc`原生产定向，保持四B/U×C组合和共同copy成本 | partition4条+directed1条；不能替代Lane5全部独立门槛 | 5条计划，NOT_RUN |
| 入口和发布身份 | build_r0_1.py锁定Core62与R0 pybind11；原source/build路径，48GiB+2GiB/64GiB minima、8GiB lease、2jobs；失败日志/退出码/sha保留 | 新输入/test exe哈希、21条命令、断言flags检查、源/依赖最终clean检查、post-lease复核；不授予科学资格 | 13项Python工具测试PASS，零实际准入尝试 |

原生Tag时间仍带memcpy排序offset；bank时间来自gpu_sim_cycle+gpu_tot_sim_cycle。host prefill不领取定时bank grant。候选只允许硬件quiescent且所选owner clean的untimed prefill；dirty/active路径拒绝，不能暗中当免费WB。数据证据是符号sector版本与requester身份，不是SASS数值payload验证。

需要Lane5显式独立核查的差异：其较早a945候选为initial-only；官方62候选明确包含后来quiescent epoch的clean prefill测试。r4/r5指定静态目标62，本轮未改其语义或擅自换回a945。应在准确官方二进制上核查该生命周期和测试预期；若需要改变科学scope，停止受影响部分并审查，不能以旧候选测试PASS代替。

当前源级检查不能证明C++可编译或所有fixture断言可达。唯一正式build后发现的普通编译/fixture问题由Lane1修复并发布新revision；不覆盖旧候选证据。Lane5另核physical_bank_clock、memcpy_payload_identity与原九项受影响生产门槛，正式应用新key须绑定新binary/source。旧R0/R1执行终态和历史fixture PASS不能恢复六条已撤回应用的科学接受。
