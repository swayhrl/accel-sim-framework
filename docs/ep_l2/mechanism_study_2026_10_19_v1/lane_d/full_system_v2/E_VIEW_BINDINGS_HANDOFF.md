# 给E：复用现有接受台账的显示绑定

不建立第二套验收或调度器。D分析沿用canonical accepted_pairs/results、原qualification（INDEPENDENTLY_QUALIFIED）、独立全输入检查和撤回/hold。

A/E冻结最终共同版本之后，E可在现有台账挂一个小的full_system_v2_analysis_bindings path/sha256指针（或交付等价精确映射，D按实际发布字段适配）：

- owner=E，authority=b2e5328aca825d6e9ebfe09e46fa208957834636；同一个qualification_id及source_identity（Core/Framework/vendor/binary），固定策略fixed_policy_sha256。
- full_victim_semantics=CLEAN_DIRTY_PENDING_INFLIGHT。CLEAN_ONLY不能叫F。
- condition_profiles：MATRIX_32.condition_id → 该qualification.supported_profiles中的真实profile名。
- pairs：COMPARISONS_AND_INTERPRETATION.comparison_id → {pair_id: E已有accepted_pair ID, left:条件ID, right:条件ID}。left/right给定科学方向，不取最有利倒数。

主图比较ID示例sad__S__F、convolutionSeparable__S__F；去一项示例convolutionSeparable__F_MINUS_R__F。使用现有接受端点、同source/input完整配对与nonresearch_config_equal=true，不为图额外启动baseline。E每接受一对给D确切事件后，D只执行一次 /usr/bin/python3 util/ep_l2/mechanism_study_lane_d/full_v2_analysis.py --render。

所有主图行必须归属于同一最终发布与固定政策；若E需要多个独立qualification覆盖不同profile，则在其正式格式发布后D增量适配精确逐条件qualification映射，当前不自行假定其有效或绕过hold。跨宿主机执行身份与动态库差异由E最终资格记录，不能只凭GPU配置相同。

V2授权40为累计总额；旧四预登记中preserve_budget=24是当时历史合同字段，字节保留，当前授权通过V2增量覆盖，不需重写历史或重置原selection时间。E接受修订后消费MATRIX_32，原14准备保留但不自动跑。
