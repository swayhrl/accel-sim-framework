# Ada架构兼容性追加说明

NVIDIA区分cubin二进制兼容和PTX JIT兼容：直接cubin兼容限相同compute-capability major的较低或相同minor，例如8.6到8.9。SM70 cubin不能原样当作Ada原生二进制；包含compute70 PTX的旧应用可以在Ada经JIT重新编译，须核实际加载架构/代码后另行采集。旧SM70 trace不会因此成为4080 trace。

官方来源：https://docs.nvidia.com/cuda/ada-compatibility-guide/

冻结试点README中“4080可运行旧cubin”的概括须按此限定。冻结payload不改写，原SHA与manifest保持；此说明作为追加材料保存。GPU UUID、actual loaded cubin、embedded PTX、source/input版本和producer契约应分别登记。旧59行矩阵中57项仍为GPU来源未认证，不能算4080正式就绪；header与目录名称不是GPU来源认证。

用户已进一步授权批量补齐及模拟器语义验证，完整执行范围见主库ACTIVE_SCOPE_20261024.md。本次单Vector试点不代表扩展任务完成。
