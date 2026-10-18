# AG2 CPU-only loader manifest qualification

结论：[AG2_EXECUTOR_CPU_QUALIFICATION_PASS](LATEST_REPORT.md)，仅授予本包限定CPU资格；模拟器启动数0，新增预算0。

- [修复边界及逐项差异](ROOT_CAUSE_FIXED_BOUNDARY.md)
- [文件角色合同](MAPPING_ROLE_CONTRACT.md)
- [真实早期系统loader证据与覆盖边界](EARLY_SYSTEM_LOADER_CPU_EVIDENCE.md)
- [正负用例及退出码](NEGATIVE_CASES.md)
- [源码、ELF与历史SHA绑定](SOURCE_AND_SHA_BINDING.md)
- [无模拟器启动证明](NO_SIMULATOR_STARTS.md)
- [未来独立cohort前置条件](NEW_COHORT_PRE_REG_PREREQUISITES.md)
- [机器可读结论](QUALIFICATION_RESULT.json)、[源码白名单](SOURCE_ALLOWLIST.tsv)、[包文件SHA](FILES_SHA256.tsv)

只修改这个新pack，tools/为CPU候选代码；history/内的旧发射器只保存为不可导入的.py.txt，未重新发布旧执行器。原9项重放的最小兼容模块不包含进程API。构建命令、编译器SHA和静态readelf输出见evidence/cpu-final/CPU_BUILD_RECEIPT.json；CPU二进制与外部raw不进入Git。
