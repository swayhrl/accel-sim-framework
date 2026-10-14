# Round A49｜A47R1 C0独立审查：确定性dtype断言缺陷与正常首次附着warning

**审查者：ChatGPT／AI-ARCH Discovery；2026-10-15。Git协调起点：`8336532bb9d888b931896a32cc45b2dae7558c27`。** 本轮只通过GitHub读取已提交真实执行日志/测量/代码、cuVS v26.10.00官方冻结源码，并用CPU端普通NumPy显示类型的str形式；没有SSH 109/174、触碰共享GPU锁、运行CUDA、下载或修改任何原执行分支。

## 0. 独立科学结论

**`A47R1_EXECUTION_STOP_ACCEPTED / C0_RETURNED_AND_SYNCHRONIZED / QUALIFICATION_ASSERTION_DETERMINISTICALLY_DEFECTIVE / INDEX_VALIDITY_UNRESOLVED / C1_NOT_RUN`。**

- **接受程序和合同层STOP**：冻结原环境/旧文件123 hash/mtime核验，两个GPU子进程（第一个元数据formatter失败、零构图；第二个C0唯一一次真正构图），GPU锁累计1.590239s，内存与新文件占用没有超限；C0返回、完成`res.sync()/deviceSynchronize()`，没有新的SIGSEGV；C1没有运行，按当前进程次数/资格合同合理STOP。
- **必须纠正的科学口径**：原执行报告标`DEFAULT_API_STILL_FAILS`反映其**预设断言未通过**，**不能被读作默认资源下的CAGRA原生构图发生了平台/API失败**。原断言包含一个由本机冻结Python源即可证明不正确的dtype字符串比较，**即使一个完全合格的FP32索引也无法通过**。同时只有单个合取assert，没有逐字段值，无法判断是否还有其它失败属性。
- **原warning不等于构图错误**：`The new dataset dimension (100) does not match the index dimension (0)`在C++已有**合法首次附着路径**中可以发生，不是断言`idx.dim==0`的实测证据。是否确实还有index维度、大小、degree缺陷，现有退出时日志未知。
- **C0相对A47有实质进展**：先前固定`PoolMemoryResource+非默认stream`路径进入`cuStreamGetId`后SIGSEGV；A47R1默认资源/default stream使小型`cagra.build`返回且同步。**两个资源维度同时改变，不能据此判断究竟是pool、stream或二者交互；C1未运行，stream敏感性UNKNOWN**。
- **仍无科学检索结果**：GloVe真实图、索引save/load、GPU search/recall、B1/B256 AUTO/SMALL性能仍未执行。不得称CAGRA GPU平台完全合格或体系结构研究假说成立/不成立。

## 1. 固定Git身份和审计边界

| 条目 | 可独立读取身份 |
|---|---|
| A47R1 branch | `hrl/aiarch-a47r1-cagra-stream-mr-minicanary-109-v1` |
| Goal/start parent | `25b04ce3bc00f82d684de905870fd93c8942830d` |
| 提交、tree | `13ea8acc7f19d13eca0aa3c049984db5c4256e83` / `adf4059ef969e7057961a54491263ddb9a5329e2` |
| 原报告blob | `dc885e75daed1b391bca9b2ed7a19ddcb7aca2e10` |
| 源代码blob | `tools/aiarch_a47r1/minicanary.py` = `e5e301b876d224a9465afb9cb3472792b1a6b323` |
| stdout日志blob | `raw/C0.log` = `477cb8af1a09c346cddf253e1a5ea9ef1db99a48` |
| 审计 | parent→branch ahead1 / behind0，15项新增文件、无旧科学结果修改；远端final commit→branch identical；Git-data tree和上述blob复核 |

[固定原报告](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/FINAL_REPORT.md)；
[原始日志](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/raw/C0.log)；
[原minicanary](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/tools/aiarch_a47r1/minicanary.py)；
[门控](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/GATES.json)。
原报告和全部raw保持不变，下面是独立纠偏，**不是事后把原STOP涂改成PASS**。

## 2. 确定性问题一：合取断言的dtype条件永远不能以合法FP32返回值PASS

原冻结程序：

```python
buildcalls += 1
idx = cagra.build(params, ds, resources=res)
res.sync()
cp.cuda.runtime.deviceSynchronize()
assert idx.trained and len(idx) == 1024 and idx.dim == 100 \
       and idx.graph_degree == 64 and str(idx.dtype) == "float32"
```

cuVS固定源码`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`：

- `python/cuvs/cuvs/neighbors/cagra/cagra.pyx` blob `27880c8dd63e1d59a53c7e0cfbcbc8aef2727ae7`：`Index.dtype`返回`dl_data_type_to_numpy(self.index.dtype)`。
- `python/cuvs/cuvs/common/cydlpack.pyx` blob `aa3fbae5f2354491d0f817edecc64a5d962d4eca`：FP32分支**直接返回`np.float32`这个类**。
- Python/NumPy字符串表示`str(np.float32) == "<class 'numpy.float32'>"`，不是`"float32"`。本审查本地NumPy2.3.5纯CPU检查同样成立；**真正的证据是冻结cuVS源码，不拿本地NumPy版本冒充109的2.5.4 runtime**。

因此最后这个测试表达式对正常FP32索引也为False。合法比较应为`np.dtype(idx.dtype) == np.dtype("float32")`或`idx.dtype is np.float32`。但原合取短路可能更早失败，**不能仅凭这个缺陷断言实际失败的一定是dtype这一项**。正确做法是先逐字段记录`trained,size,dim,graph_degree,dtype_repr,dtype_normalized`，再执行正确定义的单独校验；其值当前都没有可靠独立回读。

**该dtype断言缺陷也存在于前A47原`tools/aiarch_a47/native.py`的build资格式，但前A47在更早的SIGSEGV处已停止；不能由此反称前A47崩溃不存在。**

## 3. 确定性问题二：dim=0 warning来自合法可能的构图内部初始化

- 冻结C++ `cpp/include/cuvs/neighbors/cagra.hpp` blob`b17fb8165af43f450bad7798b9ced90243bb38e9`：Graph-only索引构造使用空`dataset_{}`，`index::dim()`在普通路径读取`dataset_.dim()`，因此首次附着前可以为0。
- `cpp/src/neighbors/cagra.cuh` 中，密集GPU build路径在`attach_dataset_on_build`默认为true时，执行`idx = update_dataset(..., std::move(idx), dataset)`。
- 同一文件`update_dataset`比较新数据维度与**旧index**维度，不等便输出`RAFT_LOG_WARN`，然后**仍构造并返回**`new_index(res,std::move(cagra_index),dataset)`。这个warning是输入附着前后的比较，**不是后置`idx.dim`自动失败**。该文件本轮固定源码经GitHub回读并核至实际warning模板。
- `cagra.pyx`的`cagra.build(params, Dataset)`路径遇到`is_owning=False`还可能进入`_attach_device_padded_from_dlpack`再附着一次；原A47R1记录了`padded Dataset.is_owning=false`。因此日志未给出索引属性的最终读数，不能把可能的正常WARN无条件归因到单一内部执行阶段。

**最强可被当前材料支持的事实**：默认路径的小build调用没有抛出异常/发生SIGSEGV并完成了设备同步；随后Python合取校验失败。不能声称构图正确的全部API契约已PASS。

## 4. 对后续最小工作的建议（拟议，非授权）

**首选科学投入：一次真正的“合法索引属性确认＋条件stream对照”，而不是第3轮平台全面重建。**

如用户另外明确同意一个新`A47R2`，建议：
1. 事前完成纯CPU静态检查/日志脚本预验证，防止`None.__module__`之类的元数据错误再次消耗GPU子进程；不引入新版库。
2. 固定旧合法输入/26.10环境，C0用同一个tiny`1024×100` Dataset包装与默认stream/default RMM，**在assert前分别打印每一项index属性、对象dtype的`repr`和标准化后值以及同步状态**；用`np.dtype(idx.dtype)==np.dtype('float32')`判定。若本次C0确实完整PASS，才进行C1，只更改`Resources(stream=非默认CuPy stream)`，仍只执行一个小图。
3. 每项一独立fresh process、一次build，非阻塞原GPU锁，总≤300s（实际通常更短），独立预算/工作区、无依赖下载/更新；**不得复用已STOP R1额度**。若C0仍有真正的size/dim/degree/训练态错误，保留属性和错误，STOP；若C0合格C1失败则报告配置敏感，不宣布vendor root cause；两者都过也不批准完整GloVe/4点。
4. 任何额外配置矩阵、驱动/版本重装、另一个完整构图/质量/性能，都需要新的科学理由和权限；不为追求“完美复现”无期限修第三方框架。

**本轮没有新GPU、模拟器、机制或模型执行，只有源码/Git独立审查。** A47/A47R1历史STOP与锁收据冻结；A33/A43 ANNS问题及点云稀疏卷积备选继续存在，未产生新的AI-ARCH硬件因果发现。