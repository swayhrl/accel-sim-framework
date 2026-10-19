# AG6 preparation and resource hold

**六点新预算已授权；0/6实际启动，预算6次全部未消耗。CPU路径通过；执行性预注册HOLD。**

固定顺序为BASE_GEMM、BASE_Gaussian、AE_GEMM、AE_Gaussian、AD_GEMM、AD_Gaussian。两BASE全部新测，不导入AG3 GEMM或AG4 Gaussian；历史T1-C仅校准参考。新BASE必须自然exit0、完整原输入、全部effective options与公共指标/traffic严格一致，分别精确校准1,071,405和3,278,356 cycles。BASE或其它科学硬失败整批STOP，不重试、不替换；完整strict通过的负性能仍继续。

独立Framework工作树已建立；保留AG5的进程实例修复，接入发布能力验证后才允许SIMULATION。生产runner的配置复制、exclusive start、能力校验、guard、实际早期loader映射、生命周期、资源采样、输出和异常路径以CPU小程序验收。该测试明确替代出版/准入/GPU strict适配器，没有把CPU结果冒充真实模拟。新增双BASE/六点预算门槛测试拒绝失败BASE、旧UUID/错UUID、缺少第二BASE及第七次启动。

CPU检查87项通过：14项真实生命周期、4项纯身份/外部负控、6项完整guard generation负控、14项生产runner CPU路径、10项配对BASE/预算门槛、18项strict破坏负控、8项mapping角色、10项原R2资源规则、3项准备HOLD负控。PID reuse由显式synthetic generation输入覆盖完整分派路径，未强制Linux内核实际复用PID。详见逐项JSON，未覆盖范围不提升。

首次现场I/O full PSI avg10为36.64%，超过25%；磁盘也低于10GiB。中间一组≥10秒双采样中I/O与authority通过、磁盘仍失败；最终一组双采样中I/O再次超过25%，末样27.53%，磁盘5,345,337,344 bytes（约4.98GiB），authority通过。**当前磁盘和I/O都不合格**，详见`CURRENT_SITE_AUDIT.json`及对应FIRST/SECOND原始快照。没有降低阈值，也未删除历史或外部项目文件。

完整511个成员约1.99GB的重新SHA扫描、当前正式runtime/loader/cache角色freeze按原资源合同保持DEFERRED；没有开始trace body扫描。已准备的清单、完整命令/CTA/instructions、270项预期options、配置及原构建身份在`PLANNED_SIX_POINT_IDENTITY.json`和`inputs/`中，明确标为计划与历史来源，不能宣称新实际输入已复核。正式新UUID尚未生成；三项HOLD负控确认资源/输入资格不闭合时不生成UUID、不fork、不读body。

资源恢复后无需再次授权这六点，可继续同批次：重新核当前所有项目/authority/FLOCK、两次R2准备检查，完成完整输入SHA及实际runtime/702项源码身份freeze，核CPU发布SHA后生成6个唯一新UUID，提交/推送/回读完整执行预注册。每次真实启动前再独立两次≥10秒准入。只有上述全部闭合才可启动；当前没有后台dispatcher。

历史永久保留：AG4为2/5实际启动、1项完整strict观测、0优化性能结论；AG3为2/6启动、1完整PASS；AG为1/8启动、0完整PASS；AA5为1/4启动、0完整PASS。新数据不会填旧四格。Core无修改/重建；未触及K1、AC/AC2/AF、其它输入、Tag候选、组合方案、native/GPU工具、论文v0.17、旧44行或GM12。当前所有性能与机理指标均UNAVAILABLE。
