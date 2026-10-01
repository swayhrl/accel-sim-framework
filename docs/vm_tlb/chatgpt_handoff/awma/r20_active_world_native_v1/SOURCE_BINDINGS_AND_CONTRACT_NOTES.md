# R20｜固定源码事实、设计选择与待核事项

2026-10-01。以下区分ChatGPT本轮实际回读的源码事实与新实验选择。没有109 runtime或asset字节验收结果。

## 1. 来源

MuJoCo Warp：`google-deepmind/mujoco_warp@3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`。

| 路径 | 固定blob | 本轮核到的事实 |
|---|---|---|
| `pyproject.toml` | `f175e4f57365c33e946e8348fcc64ec9b92b0c2f` | source声明mujoco-warp=3.14.0，Python>=3.10、mujoco>=3.12.0、warp-lang>=1.15；uv指定NVIDIA与MuJoCo包索引 |
| `mujoco_warp/_src/cli.py` | `d23ddf6b158c72da874c42d43895bf7099cfe4cd` | replay用`load_trajectory`恢复初始状态/控制中心；`unroll`捕获物理函数；每step调用`_ctrl_noise`再replay图；默认noise_std=0.01、noise_rate=0.1 |
| `benchmarks/unitree_g1/scene_hfield.xml` | `9f1e8e20ec2eff9fd097ae781696347a8036d535` | include `unitree_g1_mjlab.xml`，terrain读取`hfield.png` |
| `benchmarks/unitree_g1/unitree_g1_mjlab.xml` | `43cce5a35951aff0e94eb5be0857e8a9b8385e2d` | timestep=0.005，iterations=10，ls_iterations=20，integrator=implicitfast，eulerdamp disable |
| `mujoco_warp/_src/solver.py` | `090061796792f4d11408eaa69b4ef3c44465c705` | Round20已核：ctx.done / nsolving / capture_while、原world维度发射、incremental/stable-state与sparse/compact优化 |
| `benchmarks/unitree_g1/__init__.py` | `5514387317a2a00b1b95cebc930a2e1d948444d2` | Round20已核：G1 hfield + shuffle_dance.npz，作者nworld=8192、nconmax=48、njmax=192；Menagerie固定revision |

Menagerie资产：`google-deepmind/mujoco_menagerie@affef0836947b64cc06c4ab1cbf0152835693374`。

原始URL：
- https://github.com/google-deepmind/mujoco_warp/tree/3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5
- https://mujoco.readthedocs.io/en/latest/mjwarp/
- https://nvidia.github.io/warp/v1.16/user_guide/runtime.html
- https://nvidia.github.io/warp/v1.15/api_reference/_generated/warp.capture_while.html

网页只说明能力，实际执行依赖必须按固定源码/lock解析后冻结。

## 2. 两个会改变runner写法的事实

### 2.1 官方replay不是无噪声的完全克隆

固定`cli.py`中的`_ctrl_noise`使用`halton((step+1)*(worldid+1), actid+2)`，并按步长、noise_rate和上一ctrl做指数平滑/裁剪，控制中心来自回放。

因此初始物理状态虽可能复制，多world后续控制在作者默认规则下已可能不同。**本轮不先额外制造随机world，不先做按求解次数挑选的phase拼接。**沿用作者默认控制生成规则，记录实际ctrl哈希；只能称“作者benchmark的回放加确定性控制扰动”，不能称真实部署RL策略分布。

若本实现复用/重写runner，必须验证前若干step生成的ctrl与原`_ctrl_noise`逐bit一致。不能只设置seed=某值却忽略实际Halton规则，不能把center数组直接当最终ctrl。

### 2.2 调用capture_while不等于已消除host判定

Warp官方说明：CUDA条件图需要相容的Warp CUDA构建和驱动（CUDA12.4+能力）；未处于图捕获/replay路径时，capture_while也可在CPU检查条件。

因此本轮必须同时证明：
1. 实际GPU图中包含所需条件控制；
2. 正式iteration没有`.numpy()`/device scalar host read往返；
3. 核心测量replay同一预捕获图，不逐step重新捕获。

不强行指定当前网页的最新Warp版本，优先使用固定repo中兼容SM89且可取得的lock/依赖解析结果，生成本轮exact环境receipt。

## 3. 设计选择，不是作者实验事实

本轮默认B=1024，内存资格不足才按512、256单向回退；不是性能扫描，也不声称复现作者8192-world吞吐。

仅一个G1 hfield场景、一个公开回放；最多使用其前512个控制step。数据长度核实后按Goal公式固定发现/验证窗口；不得按solver行为或时间移动窗口。

物理iterations=10、ls_iterations=20等保持作者文件值。ITERATIONS/LS_ITERATIONS上限停止与容量overflow不同，报告单列；达到上限不能宣称收敛，也不为了制造/消除长尾改容差或迭代上限。

容量安全允许一次、只针对真正溢出的容量项扩大到原值2倍，之后重新冻结所有比较的baseline；不能用同一份已被截断的状态继续。其它科学边界变化需STOP审查。

## 4. 待Lane F实际核清

- NPZ、hfield与include mesh文件的真实字节/哈希，`load_trajectory`恢复字段与控制长度。
- exact MuJoCo、Warp、CUDA运行时/JIT编译器与SM89兼容性；不能拿source版本字符串当runtime验收。
- 编译后实际solver、cone、Jacobian/sleep/compact路径；不凭默认值猜。
- qpos/qvel/act/qacc_warmstart/ctrl以及其它跨step可读状态恢复是否完整。
- baseline可重复性、停止原因、容量overflow、目标活动集合是否真的收缩。
- 一个局部在线worklist/有限worker诊断是否足够小且保持每world必要算术。

未核内容保留UNKNOWN，不补造hash，不先承诺性能结论。
