# Index point and legacy-delta audit

机器收据：`INDEX_POINT_AUDIT.json`；可复核脚本：`scripts/audit_index_points.py`。四个既有生产文件移除精确AE增量、将三处set调用恢复为原mod表达式后，逐byte恢复固定X2。其它生产文件未动。

|调用点|统一方式与证据|
|---|---|
|OO `try_serve_tag`|`tag_set(address)`→set%banks；CPU arbitrary-line digest、4bank grant/同bank拒绝通过；bank未被row hash改变|
|OO `find_tag`|`tag_set(line)`，组内way扫描及完整tag.line==line保留；原命中LRU更新保留|
|`will_new_miss` / LDST lower候选预查|函数体与父Core相同，继续调用有LRU副作用的find_tag；OFF逐请求输出和专门victim测试确认旧recency顺序|
|OO `select_victim`|同一tag_set，组内first-invalid/min-LRU，ways、tie顺序不改；实际CPU组内victim测试通过|
|`access` / new-miss / Tag eviction|完整access函数体与X2相同，由find_tag和select_victim到同一组；Python独立LRU模型逐请求核Tag entry位置/地址/recency与miss/eviction|
|`service_entry::prefetch_next_tag`|函数体不改，仍调用同一OO try_serve_tag；grant只存cycle，Tag读延迟不改|
|K1 `invalidate_lookup`|完整函数体与X2相同，全m_tags线性遍历；late waiter/partial metadata/E后同址新allocation/old Ref保留CPU用例通过|
|IO、PAPER_BASE、MODERN|原索引字节不变；生产init和直接API的ON拒绝，OFF保留旧边界；未转用OO hash|
|ordinary C+|gpu-cache.cc/h逐byte与X2相同；没有C+ hash、更大cache或其它调参|
|生产选项及构造|shader config新增bool，gpu-sim注册同一helper；LDST init在创建frontend前检查mode/finite/geometry；仅向选中OO的config拷贝flag；custom-cache入口ON明确STOP|

最后一项是静态集成审查，实际编译/运行的是生产header和生产option parser。受两次编译预算限制，没有构建新libcudart、完整Core或trace executable；不声称完整生产翻译单元已编译、动态绑定已验证或完整LDST/应用cycle已验证。

替换语义整理清单：**NONE**。唯一策略变化是ON的固定set index。新增mode/geometry检查与flag传递均为该策略的范围约束；未把任何探测LRU修复算入hash收益。既有K1失效、source observer、普通pending invalidate、finite服务、allocator、WB和ordinary C+源体不变。

`CORE_DELTA.patch`为零context审查副本；应用时使用`git apply --unidiff-zero`。
