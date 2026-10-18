# CPU正负资格

最终结果34/34：3个正例exit0；31个明确拒绝exit42。逐case实际argv、stdout、stderr、expected/actual exitcode和reason完整保存在evidence/cpu-final/MAPPING_ROLE_TEST_RESULTS_V2.json，简表见NEGATIVE_CASES.tsv。不是仅把异常捕获写成逻辑退出码：每项由独立/usr/bin/python3进程运行，父驱动检查真实returncode与精确原因前缀。

正例为已注册cache匹配、全128快照早期出现再unmap、合法重复完整快照。负例覆盖cache遗漏/错hash/错身份/路径/dev/inode、未知ELF与非ELF、缺角色/错分类、ELF冒充loader数据、动态库SHA、cache可写/执行、deleted路径、晚采样遗漏cache、未见unmap、错误exe、未资格无cache模式、未知伪映射及坏格式。

文件变化负例在AG2私有fixture实际执行：冻结后改内容、哈希期间改内容、哈希期间同内容新inode替换、确认前unlink或替换。使用生产file_record/verify_file，受控hook仅插在测试的digest返回后、post-stat之前。哈希不符用实际系统cache/库读取后比错误冻结digest，并用私有data副本补实际内容变更；没有修改/etc/ld.so.cache或系统库。dev/inode/path等异常由保存的真实CPU maps单字段扰动重放；未知ELF/nonELF由真实已观察文件移出候选表，未伪称在live进程映射新恶意库。

保留早期工程结果：第一次负例driver执行后因Python缺file_digest未写出逐项结果，其逐项返回码UNAVAILABLE，driver exit1保留在ENGINEERING_COMPATIBILITY_RECEIPT.json。第二组34项有完整记录，32/34符合预期；另外两项也拒绝但未到预定分支。fixture修正为单行伪映射及不同大小内容，再运行最终34/34，旧结果不覆盖。生产规则未放宽。

无cache主机的合法正例、额外KNOWN_READ_ONLY_DATA live映射、其它系统平台未触达，标UNQUALIFIED/PARTIAL，不纳入本轮通过项。所有被计PASS的用例均实际执行。
