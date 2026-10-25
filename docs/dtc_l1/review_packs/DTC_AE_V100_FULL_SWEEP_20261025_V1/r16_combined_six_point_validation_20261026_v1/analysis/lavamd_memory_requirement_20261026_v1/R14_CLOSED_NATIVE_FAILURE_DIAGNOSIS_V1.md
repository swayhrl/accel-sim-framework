# R14已闭合native失败诊断

本次cutoff实际查到2个closed native失败。没有从粗略stop_reason套用旧freshness归因。

## E2-AEREPAIR-ddb6806316876a85-CH-V1

UUID `520eccae-e73a-4e37-a480-6413a65e39bf`，elapsed 126.148985337466秒，rc=1。raw明确`std::bad_alloc`与SIGABRT，栈在`vector<inst_trace_t>::_M_default_append → get_next_threadblock_traces → init_traces → issue_block2core`。

18条连续authenticated progress已刷新到约120秒，最大间隔10.001410038秒，completed仍0；因此旧heartbeat缺口已修复，这次不是30秒stale。RSS最后采样16680747008 bytes；冻结AS/RSS上限16GiB，外部RAM/disk采样均PASS、原policy未STOP。

## E2-AEREPAIR-ddb6806316876a85-CM-V1

UUID `615d93c5-a990-4714-932b-9eac0b3ae6c9`，elapsed 126.02797672711313秒，rc=1。raw明确`std::bad_alloc`与SIGABRT，栈在`vector<inst_trace_t>::_M_default_append → get_next_threadblock_traces → init_traces → issue_block2core`。

18条连续authenticated progress已刷新到约120秒，最大间隔10.00220231秒，completed仍0；因此旧heartbeat缺口已修复，这次不是30秒stale。RSS最后采样16680747008 bytes；冻结AS/RSS上限16GiB，外部RAM/disk采样均PASS、原policy未STOP。

容量证据：单kernel最多9CTA/SM，固定CTA槽0..8映射warp0..35，64SM最多2304个曾填充的text向量，不是4000个full-grid warp全部驻留。完整header索引420346376 records与完整输入SHA闭合；max CTA516955 records，sizeof248，保守vector capacity68.774GiB，另有memadd heap及runtime/allocator开销。capacity不等于RSS。

新独立有限2point请求使用hardAS/RSS128GiB与预计物理96GiB的资源门，优先单路，保持48GiB cgroup/64GiB host实际余量。当前16GiB源/spec/UUID、失败账本与archive保持不变；不重跑spent UUID、不把新验证并入原288性能点。

详见本目录MEMORY_REQUIREMENT_SUMMARY_V1、PHYSICAL_WARP_CAPACITY_BOUND_SUPPLEMENT_V1与R14_CLOSED_NATIVE_FAILURE_DIAGNOSIS_V1 JSON中的SHA、完整采样、源码行与限制。
