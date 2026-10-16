# Lane6论文/PPA r4（消费协调review_r4+r5）

Authority `77a9fbe937ea23465cf0d0076d2df1909f52d055`：按顺序读r4 PARALLEL_CONTINUE、
r5 CONTINUE，以r5裁决。原Goal/分支延续；正式48GiB准入不阻止本轮轻量工作。

本revision实际交付：

- PAPER_DRAFT_ZH_V4.md与paper_4page.pdf：完整四页中文双栏工作稿，生命周期、
  WB共享因果链、独立资格、条件性归因对照与成本；非官方ISCAS模板或可直接投稿的最终版。
- PPA_LEDGER.md、FIELD_COST_LEDGER.csv、COST_MODEL.json：精确未编译Core62dc候选，
  9处源字段锚点，6个显式参数场景，比较逻辑和关键路径责任；无mm²/mW/STA估算。
- CONDITIONAL_EXPERIMENTS.md与RESULT_AND_FIGURE_SLOTS.json：对接Lane5十条不执行的
  准备行和结果槽；三类因果分开。静态重划分/copy/headroom只作条件性设计，不授权新配置。
- current_pair_intake.py：Lane5原生V2 API桥接，保留r3原生CSV/PAIR、raw/config/
  executable和十一门槛校验。动态新withdrawal、完整十字段identity和proof由Lane5
  API裁定，替代r3自定义CURRENT_ACCEPTED顶层/matrix假设；原r3程序/文件不修改。

当前CURRENT_ACCEPTED正式pair=0，mean=null、性能图=[]。旧R0/R1六次原始执行及
r1/r2/r3保留；撤回附录在r3，不因新稿、source适配或producer PASS解除。历史13行
locality和旧静态1.721259倍诊断只按原范围引用，不重复原仿真、oracle或校准。

复现：ReportLab4.2.5（可装到独立临时目录）、系统字体Droid Sans Fallback与
DejaVu Serif。这里只编排小型文档，不调用生产构建入口或申请仿真配额。

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/render_paper.py \
  --reportlab-path REPORTLAB_SITE_DIR --output-dir NEW_LAYOUT_DIR
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/audit_costs.py \
  --core-repo READ_ONLY_CORE_REPO --output-dir NEW_COST_DIR
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/test_v2_bridge.py
```

新V2桥接12项测试，不重跑Lane5的62项或Lane6 r3的30项。实时只读审核：

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/audit_v2_current.py \
  --framework-repo FRAMEWORK_REPO --output NEW_AUDIT_JSON
```

新正式pair的adapter须绑定实际官方qualification_publication/path、producer
publication/contract_path与native_pairs准确publication/path。执行current_pair_intake.py
时强制实时fetch当前Lane5分支，绑定V2 manifest、generation、proof和最终ref复核；
失败无缓存回退，不修改launch authorizations或registry，也不把其当结果预接受。

Source/receipt/进程/资源快照和实际测试范围在SOURCE_MANIFEST及validation/。
七个外部DTC模拟器仅被观察，进程、文件、配额均未操作。本Lane不参与Storage-Ops，
不删除或归档研究资产，不改变48GiB或构建路径。STATUS/RECEIPT留在原Lane6目录。
