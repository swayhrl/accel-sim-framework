# 第一批：main61 W_ONLY / F_MINUS_R

交E2独立资格审查的具体配置已经准备完成：Conv、CFD、DWT各两项，位于各工作负载子目录。`BATCH.json`是入口，逐项绑定profile、完整有序config、source/main、已接受S/F资格、输入、parser和静态检查。`SPEC_CANDIDATE.json`明确包含无效的待审资格占位符，不是可派发队列，不能据此启动应用。

| A/E profile | W/V/T/M | source-supported | 当前工程控制 | E精确profile资格 |
| --- | --- | --- | --- | --- |
| W_ONLY | 1/0/0/0 | 是 | 静态配置、固定几何、非研究参数与资产hash检查PASS | 未具备；现有输入资格只登记S/F |
| F_MINUS_R | 1/1/0/0 | 是 | 同上；完整clean+dirty TVD，非clean-only替代 | 未具备；现有输入资格只登记S/F |

这批没有RO证书新增需求。配置关闭T/M并移除RO证书参数；保持ft_mode=2、WBUF16、payload1168、D512、per-address32、LineMSHR128、WAD/TVD128、4bank/P1、observer=1与原DRAM/ROP/L1/trace配置。W_ONLY不是S：保留统一WB生产路径；F_MINUS_R保留完整V，不改变W或资源总量。

可复用内容：正式A2 main61发布、E已接受输入的完整native opcode/输入语义证明、同main61的OFF与原11+7资格门、17项受影响原生证据及对应source/path审查。W_ONLY尤其对应现有d010原生A1 mode2、bank retry、legacy credit rollback证据；F_MINUS_R对应现有dirty WAD128、capacity/partial dirty、clean matched TVD、warm/drain证据。原生回执入口为正式发布目录`MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/NATIVE_EVIDENCE_MANIFEST.json`。这些回执不能自动变成新的完整应用profile资格。

E最小处理：先审查上述精确原生证据是否覆盖新profile；已有覆盖无需为这批准备重复17项测试。若配置组合或需要的分支确未被覆盖，仅用现有d010 native ELF补相应单项；不重编完整模拟器。随后明确发布包含该输入、该profile、准确feature/ideal vector、parser和证据引用的新资格，并重算资格ID与候选spec绑定。应用前仍由E完成强制input/config复核和原中央资源/启动准入。

Conv两项已属于原32条件。CFD/DWT四项是具体准备候选；当前32矩阵没有对应消融条件，需E/D在原分配内明确审查工作负载替换，不能视为新增四次授权。六份候选不是六次启动计划。已有S/F端点能否用作新比较锚点，须由E核对输入、source/binary、非研究不变量、parser资格与完整exit/drain，不能仅按工作负载名称复用。

本批0构建、0原生测试、0完整应用启动，未修改E registry/main61。下一批单独交RO因子与诊断，不阻塞本批资格审查。F_MINUS_W和完整fixed64 dirty+RO仍不支持，不提供替代配置。
