# Lane BA / 174-new Lane T — 有限交接

本审查复用BA `061e9fb38856b8d7b330950b2a602c65d510bab9` 六条清单，Lane T `883f4a4b5ece15cff903b5c5fbe0489870532b9b` 的三份SHA PASS。没有新Goal、迁移控制器、传输器、监督器改动或模型下载。

给BA：当前原174精确元数据6/6与BA一致；126个其他文件KEEP，模型原件ACTIVE_KEEP。本审查结论为六HOLD、归属授权0，不把本审查当删除信号。归属/109未来保留尚UNKNOWN，最新109历史路径可见性缺口见NODE109_BOUNDED_READONLY.json；请保留原BA选择器边界。

给Lane T：继续原窗口及原门禁，仅核验下列pending3；不要重算RAW1–3、不要复制19.374GiB、不要放宽IO阈值10，不占用TLS P9/EP-L2 E2租约。回执请逐文件给出native164路径、执行机/namespace、实际挂载source/fstype、大小、SHA、前后stat、时间与门禁结果。RAW1–3只需复核身份仍对应原SHA回执，不重哈希。若仍无获准native164入口或现有SSHFS路由不放行，直接记录缺口，不新建轮询或绕过门禁。

| ID | 真164路径 | 字节 | 预期SHA256 |
| --- | --- | ---: | --- |
| 4 | `/home/shared/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-raw/a09a35458c702b33eeacc393d103063234e8bc28/model-00004-of-00004.safetensors` | 3556377672 | `1a72d403cdf0c1ec3cb7f289f17b394a01e64394c2e9b3c0f94dbce3faf879bd` |
| 5 | `/home/shared/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00001-of-00002.safetensors` | 3996422976 | `4ad6e70f93823a9228931615e04b5e9293854c236fb4bd5f85e27f3b600605ad` |
| 6 | `/home/shared/huangrulin/c16_ai_workload/assets/models/qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641/model-00002-of-00002.safetensors` | 1574406784 | `920a8cc9d3c81668f18014a69bb041ab8bab22a31640a713f90f5e7580e2f126` |

总计9,127,207,432 B。RAW4旧前缀不能续算SHA，须全文从0读取。三个匹配结果返回原Lane T权威分支即可，本审查随后引用新HEAD，不建立第二份完整性控制系统。GitHub协调消息送达不代表对方已接受或完成。
