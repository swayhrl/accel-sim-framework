# 源码与SHA绑定

本Lane Framework固定基底cc5f51ea068e5a234811d2fbe79a5ccdbab21769，独立分支hrl/iscas2027-dtc-lane-ag2-loader-manifest-174-v1，独立worktree=/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ag2-loader-manifest-174-v1，独立raw/build根=/workspace/dtc-lane-ag2-loader-manifest-174-v1/。Git差异只允许新增本AG2 pack，不修改既有路径。

只读Core固定965dffe04366e665626de4afeb7ffebca8622b5f，tree=b089d5838ca554679edd46476050b6d3885432d0。旧Framework与旧Core worktree均clean；旧11项runtime/loader/library的当前SHA逐项匹配原清单，见evidence/OLD_RUNTIME_READ_ONLY_SHA_RECHECK.json。没有编译或执行这些旧runtime。本轮不读取/修改AC2、AD、AE、AF或整合其代码。

候选源码白名单为SOURCE_ALLOWLIST.tsv中的7个tools文件（5 Python、2 C）；另列最小legacy import兼容模块及不可执行历史文本、工程旧版本。没有通用shell/任意target/dispatch参数。主解析器SHA=1409539bad1d173c4bf48463c5465f54e8aba89db736e27bae745fd7a7f07155；实际CPU启动helper SHA=a38ff337ecfabe18bf56d2ee5d9a51b6f1a35b83ef26d72fc508a6c6bc9b94ce，均在最终CPU目标启动前冻结。

| 当前CPU输入 | SHA256 |
|---|---|
| C probe ELF | c6eea7d96dd6a9441a8cdec7381104c0ea2dda2663631d8d686e16011c830b8c |
| CPU fixture .so | a378f9e2a9530a2921c8ffa50ef09c4023eba7553990393ae0e6e9ee002d4af2 |
| 系统interpreter | 9eb34cb2da3ae2a9398cc09b3cd2d069563ec40d9858cb711af15cd23fa80abf |
| libc | c53819710b163d3f1d2541778590d58d3ef31cb0ed75adcbe059faac68c1e72d |
| loader cache | 026c6716eea796297e7da1e0f63c3439bfa47108cf8a22fae80c59b22e9ec1ff |

CPU_BUILD_RECEIPT.json绑定C源码、gcc实际路径/SHA、编译完整命令、ELF static readelf与DT_NEEDED；CPU_MAPPING_PREREGISTRATION.json还绑定真实stat、cache预冻结时点与候选代码。二进制只留独立build root，不上传Git。最终31个拒绝和3个正例的用例源码SHA独立绑定在结果JSON与全包SHA中；工程修正未改最终CPU trace所绑定的解析器。

HISTORICAL_BINDINGS.json将每份旧文件的原commit/path/SHA绑定到本包副本；旧launcher代码仅.py.txt保存字节。原9-case重放仅import路径及输出目的地改变，逐行diff在LEGACY_REPLAY_ADAPTATION.diff。历史postlaunch cache SHA从未成为旧AG的prelaunch项。

旧AG UUID5de274d3-f296-4ee8-a577-17cc661e718e仍1/8消耗、0完整strict、0完成kernel；8份关键原run收据保留于evidence/historical-attempt-receipts/，原位置SHA前后核验，另按原FILES_SHA256.tsv核完整attempt。旧AA5 STOP_RECORD及报告为权威AG提交中的固定副本，1/4和0完整strict不变。未触碰旧锁、STOP文件、历史raw，未对其它项目发送信号。

包内.gitattributes仅对字节保真的原maps/历史证据及unified diff保留行尾空白，不改变证据字节；自有TSV使用LF。FILES_SHA256.tsv包含本包所有文件（不含其自身）的SHA/字节数。最终Git push/fetch-back逐blob与工作树核验收据在独立raw/FINAL_PUBLICATION_READBACK.json；本包不自嵌自身HEAD以避免循环。最终发布必须同时满足仅AG2目录变化、HEAD/tree与远端fetch一致、所有包blob SHA相同、worktree clean。
