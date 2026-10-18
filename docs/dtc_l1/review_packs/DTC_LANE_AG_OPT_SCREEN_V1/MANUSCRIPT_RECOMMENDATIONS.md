# 仅供后续审稿修改建议

本文件不修改现行v0.14-R1稿、旧44行或GM12。

1. 将DISCOVERY_OPT标为独立新开发cohort，保留AA5 1/4启动、0/4完整strict及其资源STOP；禁止把新BASE填旧K1四格。
2. 只有全输入strict和共同BASE校准后，才能列本轮整数cycles及对本轮同输入BASE的比值；两输入为发现集，后续独立BICG/DWT2D需先冻结配置再经用户审查，不能按结果选输入。
3. AE报告预固定bank保持hash的正/中/负结果，披露既有Tag时延内XOR假设；开发64×8不是论文主配置晋升，不能仅用hit变化代替全系统cycles结论。
4. AC若纳入，单列两有限raw-sector bank容量、端口/交错/回压和真实重叠指标；P640时额外160KiB/SM不是equal-area。AD readiness条件变化须使用其独立定义和各消费者通知人群；未通过资格的格明确HOLD。AF不进入八点，也不能凭CPU受控例声称真实输入机会。
5. 对未打印的重叠、bank冲突、K1-only、私有generation/sector收据标UNAVAILABLE；不要补零、从wall推性能或将SASS replay写成native值正确性。

本轮实测收口：1/8实际启动、0完整strict，执行器因loader cache预冻结漏项停止。所有应用cycles/ratio UNAVAILABLE；不能用CPU定向例或旧T校准值代替应用收益。AC/AE保留其有界CPU资格，应用机会尚未验证。
