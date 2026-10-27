# T独立贡献

| 实际固定延迟 CORE cycles | F−T完整cycles | F完整cycles | T speedup (F−T)/F | TagFAIL / relieve / detach / detach后接受 |
| --- | --- | --- | --- | --- |
| 100 | 77237 | 77237 | 1.000000 | 0 / 0 / 0 / 0 |
| 200 | 77767 | 77767 | 1.000000 | 0 / 0 / 0 / 0 |

PROVEN：每个同延迟对只差T开关，物理资源、完整282回显、输入、Core/ELF及W/V/M背景保持。完整cycles相等；被动资格中T禁用也没有detach尝试，不是失败detachment抵消性能收益。默认点F/L0同producer旧D复用有独立资格，其余五点是本Goal新预算的原运行。

NEW_WITH_ELIGIBLE等can_detach计数含T开关，因此T-OFF的0不能当结构RO候选消失。真实RAW TagFAIL与资格联合均0；没有经历production relieve，也没有被迫在Frontend/TVD/WAD/descriptor门禁中取消一次真实TagFAIL。不得把独立边际相乘为共现，或放松reuse_seen/ready/generation保护来得到非零。

UNKNOWN：这批完整应用未触发detach，不能提供detached旧RO返回/新Tag代际路径在真实应用中的实证覆盖；协议正确性依据同producer既有定向fixture和本轮CPU资格，适用范围见VALIDATION_AND_POSTRUN_PARSER_CORRECTION.md。无触发不等于实现错误，也不等于泛化证明无用。

决定：维持T，保留两点0独立收益结果，不增加启动、不延伸延迟档位、不改detach策略。固定延迟200为单独敏感性条件，不能称默认GPU的T加速。
