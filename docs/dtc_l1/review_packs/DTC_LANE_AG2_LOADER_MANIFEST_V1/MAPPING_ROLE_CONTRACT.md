# AG2_MAPPING_ROLE_V1

适用范围：Linux x86-64、同一mount namespace、固定单线程无GPU C CPU probe。候选库没有启动API。调用者须在完整读取maps和文件校验期间停住自有目标。本轮用ptrace syscall stops实现；未来执行器若无法提供同等早期覆盖，不得仅用晚采样取得资格。CPU harness上限30秒/2000快照，每次哈希文件上限32MiB；越界拒绝，不静默截断或自动扩范围。

每项精确绑定canonical绝对路径、角色、来源、冻结wall/monotonic时点、SHA256、设备号及major/minor、inode、size、mode、uid/gid、mtime_ns/ctime_ns、nlink、ELF类型和存在/消失规则。冻结完成并写出只读manifest后才允许固定CPU目标fork；启动前再次校验。没有路径通配、目录许可或按内容事后加白。

| 角色 | 内容与身份要求 | 映射规则 |
|---|---|---|
| ELF_EXECUTABLE | 固定CPU主ELF；ELF64 little endian x86-64，ET_EXEC或ET_DYN；全清单恰好一个 | /proc/pid/exe等于固定目标，完整快照必须含其精确映射 |
| ELF_INTERPRETER | 主ELF的PT_INTERP canonical路径，ET_DYN；恰好一个 | 每个快照必须含其精确映射 |
| ELF_SHARED_OBJECT | DT_NEEDED预声明的精确ET_DYN依赖 | 全部本轮注册依赖须在序列中真实出现；每次出现均验证 |
| LOADER_DATA_CACHE | 仅/etc/ld.so.cache，非ELF、当前glibc cache格式、独立预冻结身份/SHA | 只读且不可执行；早期必须实测出现；确认后可unmap，消失时再核文件；未见或未确认不得默许 |
| KNOWN_READ_ONLY_DATA | 仅未来逐文件显式声明、带data_purpose的非ELF | 只读且不可执行；没有此类文件获本轮live注册资格，新增必须另做明确freeze/CPU资格 |

maps每行解析范围、permissions、offset、dev、inode及路径；处理内核八进制路径转义，拒绝deleted映射、未知文件和未知伪映射。空匿名与列明Linux伪映射（heap、stack、vvar、vvar_vclock、vdso、vsyscall）记录为非文件，不算忽略非ELF文件。所有实际文件映射一律查注册表。

每个文件O_RDONLY|O_NOFOLLOW打开canonical路径，读fd前stat、实际SHA、读后stat及命名路径stat必须一致，并与冻结全部身份字段及SHA一致；atime不作为内容身份。fd身份、路径变化、删除/替换、未知role、ELF伪装数据、data可写/执行、未知文件全部拒绝。一个文件的多段映射逐段核dev/inode，每个完整快照至少对该文件哈希一次；不依赖晚期路径重新解析冒充原inode。不能证明身份即拒绝。

序列从kernel exec stop开始覆盖每个syscall前后；早期已确认cache的后续消失允许，未确认就消失不可取得PASS。自然exit0、全部注册文件曾被确认、实测cache出现及消失、最终文件身份不变为闭合条件。身份检查不证明内存中ELF字节未被CPU自行修改或任何模拟模型/数值正确性。

无cache的合法系统属于单独受控资格：当前版本cache_mode仅接受PRESENT_REQUIRED_EARLY；不存在、替换、未知格式或ABSENT模式均停止，不能创建空cache、加--inhibit-cache或假装通过。无cache主机正例未测试，明确UNQUALIFIED；未来需另列系统条件、loader解析依据、负例及用户批准的资格变更。
