# 最终状态与科研收据

**结论：维持现有T；本Goal完成，不自动启动下一轮实验或合并accepted Core。**

在同一新8d55 ELF/原trace内容/原四配置下，Vector OFF和ON均实际完成并接受：75,039 cycles、56M指令、15,625 CTA、64 slices、1 kernel、自然return0、hardware drain。完整scoped非干扰PASS；两次新完整启动额度已全部消耗，无重试退款，两请求均CLOSED、remaining0、reserve0。未继承旧epoch2余额，未关闭或改动他人的预算。

## 主要科学发现

- PROVEN：375000个唯一NEW，真实TagFAIL/relieve/detach均0；到达前同set RESERVED最多3。tick末峰最多3/16；85个set有瞬时event4/16，但area_R4=0。
- PROVEN：所有4096set整run NEW91–93，广泛分散。500000/750121 episode为0tick；但250000正寿命NEW平均1141.591732 L2 ticks，不能概括为所有预约都很短。
- PROVEN：1.5M requester及不同sector观察共享375000新Tag；RO250118、merge749882、issued1M sector，merge不是DRAM请求节省。
- LIKELY：分散、sector/RO共享和零时长RE共同限制Tag积累；L1/L2/lower队列阻塞共存。UNKNOWN：各自排他因果份额和若触发T的端到端收益。

## 实际验证与未执行边界

实际执行：清洁V2源码/编译身份核验；22次CPU组件控制/11对OFFON；2次完整应用；完整数值及64slice/32DRAM scoped NI；严格64slice wire和4096set守恒解析；一次独立离线分析；全部应用及工程归档的关闭重开SHA与两次独立原生恢复。静态路径覆盖与未逐site执行的policy/flush/atomic分开标注。

未执行：新CFD/DWT/Conv、DRAM935/MissQ32重跑、GPU/4080 trace采集、reuse guard放松、associativity/DRAM延迟扫描、T策略修改或accepted Core合并。实际数值SASS输出及真实硬件验证仍UNKNOWN。旧r5敏感性结论保持旧Core/binary身份，不与本轮拼接。

## 交付与恢复

本目录含要求的6份说明和两份各4096行CSV；EVIDENCE_INDEX.json给出全部源身份、raw/NI/native/预算及恢复证据SHA。scripts/为精确字节审查副本；不是新的执行权限，路径/原位置见SCRIPT_SOURCE_MANIFEST.json。Core源分支：[11c](https://github.com/swayhrl/gpgpu-sim/tree/11c02df1034112013523429894f1f931323adbef)。

- OFF raw SHA256：c8c41b772fc254bfb7a9410f0c56f6bba98974b6d48bd4f1ad8ab0e0a1ea02ce
  真164 bundle：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_application_v2/EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2/9d11193015c50310b462d732f5a2e39081d7ec0782b64abfab95d683eed7baaa`
  manifest SHA256：a951a587b26b19a95ea1792a28e465e22102a5778841ce73d9b2989f9bbd7351
  恢复入口：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_application_v2/EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2/9d11193015c50310b462d732f5a2e39081d7ec0782b64abfab95d683eed7baaa/RESTORE_EP_TAG_LIFETIME.py`；CLI `--destination <新的174原生ext4目录> --minimum-free-bytes <独立核验下界>`；工具会核bundle内部manifest/chunks及真实native目标。两次已验证目标见index。

- ON raw SHA256：09d6d5a254cb80c387ef8d4901e44d13993f3b0f0ebd26d5f6531d97c78a75ce
  真164 bundle：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_application_v2/EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2/b9b6596f4b66185729c84128b8b6cc183de980da17e2b8164f8fb78d3c2d4d1a`
  manifest SHA256：464466bdbb880fabc63b7fe6d8024c7f7f4bb05773dcb859f986ce6148ef79c8
  恢复入口：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_application_v2/EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2/b9b6596f4b66185729c84128b8b6cc183de980da17e2b8164f8fb78d3c2d4d1a/RESTORE_EP_TAG_LIFETIME.py`；CLI `--destination <新的174原生ext4目录> --minimum-free-bytes <独立核验下界>`；工具会核bundle内部manifest/chunks及真实native目标。两次已验证目标见index。

工程证据bundle：`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_engineering_final_90a4ccc0-b41d-4c94-a803-0f285cc0074f`。256文件、53,060,484B，压缩7876129B；manifest SHA256 `d25ec43deecf7bab37be23a4f137d0b9a5664dd09a241b769ca9a1af7aa80e32`；archive SHA256 `68389fbfef8657b072c25550e5e98de4e460a000b66111c7ddbc0db685df2ff2`。两次独立native regular-member解包均核256文件SHA，原数据保留。

工程恢复：`python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_engineering_final_90a4ccc0-b41d-4c94-a803-0f285cc0074f/RESTORE_ENGINEERING_EVIDENCE.py --restore-bundle /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_tag_lifetime_engineering_final_90a4ccc0-b41d-4c94-a803-0f285cc0074f --destination <新的174原生ext4目录>`。只恢复/验证，不启动模拟。最终Markdown/汇总CSV/代码另在独立GitHub审查分支提交；工程bundle刻意不包含引用其自身收据的最终说明，避免自引用。

大Trace及大结果始终真164；174仅必要源/build/热输出及有界恢复。完整输入约207MB双读2.684秒，无大型本地缓存需求。资源核算及SSHFS inode续资格历史见RESOURCE_GATE_CORRECTION_AND_STORAGE_REPORT.md。

## 下一决定

将T表述为有定向CPU正确性支持、在已接受真实应用中尚缺Tag容量压力机会的机制；现有加速不可归因于零触发T。无需为产生非零detach安排扫描。若未来独立授权进一步研究性能，优先隔离DRAM服务的时序与带宽因素，保留负结果；这属于新受控设计，本Goal不执行。
