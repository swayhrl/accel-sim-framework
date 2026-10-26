# 被动Tag RESERVED生命周期Observer

Goal: EP_L2_TAG_RESERVATION_LIFETIME_CAUSAL_V1。独立研究实现；默认OFF，不改变T策略。应用结论与接受/归档状态见FINAL_STATUS_AND_RECEIPT.md，实际测试与限制见OBSERVER_NONINTERFERENCE_REPORT.md。

## 精确生产身份

|对象|身份|
|---|---|
|Core|11c02df1034112013523429894f1f931323adbef；父1093d2629e3d6a9130ba25b9dd119b6f3e16c092|
|Core tree|5495ec739845b075356a8c67ff289763c56ad2aa|
|Framework runtime|9dd1ee57a83d83b56b7874bc7c716185ab52c8f7|
|vendor pybind11|f90c430c3a1ce8f08c09942a5a1c3a797bb2295b|
|实际应用ELF SHA256|8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef|
|静态libgpgpusim.a SHA256|685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4|
|Core源tar SHA256|99b876285fef26539ef464b751cdee9bcd754e8101815f57df56e830fed37a17|
|Observer header SHA256|d88efa5012f1bd24c0b55be42504c1b8e3727bcabdf46a2c96385ee61082b8e1|
|SourceQ V2 SHA256|8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814|

规范source_identity.archive_sha256指静态库，不能与源tar混称。新Core/ELF不继承旧1093/e511应用资格；A2、原native/main61和E2 r5历史谱系均保持独立。源码在独立Core研究分支发布，未合并accepted EP-MAIN。

## 观察人口与时钟

一个Tag任一sector RESERVED即计一个预约Tag。episode为同一incarnation从无RESERVED到有RESERVED，再到最后一个RESERVED消失。R→R增加sector不另开episode；已有Tag后续SECTOR_MISS重新进入为RE，新Tag首次为NEW。Tag index复用用observer generation区分；Tag incarnation、reservation episode、RO transaction、sector和requester分别计数。

age/面积以真实L2 tick计；同时保留gpu_corecycle窗口锚点，不使用replacement API的time字段。gpgpu_sim::cycle在clock_mask后、同刻其它域/ingress前为各slice准备tick；cache_cycle再次begin幂等。事件峰与tick末峰独立，同一tick内进入并退出的episode寿命合法为0。

LEFT为seed时已存在预约，RIGHT为观察结束仍未闭合；二者不伪装成完整寿命。每set必须满足LEFT+ENTER−EXIT=RIGHT，weighted occupancy area=SUM_NEW+SUM_RE+SUM_LEFT+SUM_RIGHT。完成NEW/RE各33个log2 bin：0为0tick、1为1tick、2为2–3tick、32为至少2^31tick。有限窗口Little's Law只对同slice/set同episode人口且显式处理carry，不能用全GPU平均率乘平均RO延迟预测TagFAIL。

## 生产挂钩与非干扰合同

实际mutator旁建立TLS RAII mutation context；不往共享cache_block_t增加observer字段。allocate/reset/sectorallocate/fill/set_status、flush/invalidate/TVD及9个raw block alias均在真实写入处通知，不额外调用Tag probe、directory/RO query、CAM或bank仲裁。独立merge marker防止同一attached merge重复算requester。RO初始resident ready单记RO_INITIAL_READY，后续lower返回只记新增ready位。

RO的admit/merge/issue/ready/response/retire在原生产动作之后记录。Tag RESERVED结束、RO lower-pending结束、response-only结束分别计时；不能互换为同一个latency。异常untimed prefill/不完整epoch/计数溢出/IO错误显式标invalid，严格解析器拒绝科学推广。

## 有界状态及输出

PROVEN静态与实际layout检查：observer每slice211464字节，64份加2MiB包络为15630848字节，小于16MiB；共享cache_block_t仍24字节。该结论限定当前64slice×64set×16way几何，不泛化任意配置。新增汇总输出全局上限16MiB；每slice最多8条案例；55个counter、19个stage、15个window event counter，8192 L2 tick一个窗口，无无界逐请求日志。

默认EPL2_TAG_LIFETIME=0。OFF无lifetime ledger/frame，ON新增统计不参与准入、替换、Tag选择、资源释放或cache/DRAM调度。旧EPL2_DETACH_DIAG及EPL2_TAGPRESSURE_DIAG两臂均为1，不通过额外probe补数据。完整非干扰结果必须以实际同binary OFF/ON闭合结果证明，不能由设计或CPU PASS代替。

## 统计边界

stage是各真实动作的不同单位，send/deny重复尝试、head-cycle、唯一NEW与sector不可直接相减。window只有总预约面积和窗口事件/stage计数，没有NEW/RE分类型window寿命或RO分phase window时长。stage在每slice的64set行重复，聚合需先去重。时间同窗和同时存在的限制不等于逐请求祖先链或严格因果份额。
