# C0：隔离基线与分支点验证

状态：`PASS`。

- Framework 从 `eb18c43c516bdcd52c164969df10d97b895f45f1` 建立隔离分支；Core 从
  `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` 建立隔离分支。
- 仅使用 Window C worktree 和 `/workspace/vm-m4b-speculative/` scratch。冻结
  decode1 compute-only trace list SHA-256 为
  `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`。
- 冷构建及标准 paper 三段 smoke 均成功。基线 M1--M3（15 项）和 M4C object
  attribution 回归均通过。
- 基线诊断发现一个既有的完成通知元数据被误计为活动资源，导致 quiescent
  invariant 拒绝结束；Core 提交 `aecd684158e37a78bd7d814db0ddfeafd2fc097f`
  将该判断恢复为“MSHR/lookup 均空且真实资源 invariant 成立”。修复后标准模式
  回归恢复，未改变 paging 语义。

这不是新的模型机制，也不包含 M5 工作。
