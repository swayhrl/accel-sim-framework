# Same-input/design P0依赖优先：候选未安装

本候选只包装当前`aging.original`。先对原传入pending pool调用captured generic B；原B返回HOLD则直接HOLD。原B选择非P0后，仅查本pool内唯一同input_digest、同cell的P0。P0须为已登记canonical身份、未spent/sealed/claim、无INTENT/DONE，pending成本不得低于canonical；再以同sample/claims/history/previous/policy/dispatch_index仅对[P0]调用captured完整B。成功且后验仍可用，才返回该P0自己的完整B决策；否则保留原decision。源码/原callable/21pins/ACTIVE来源证据漂移返回None。

不从全局增补P0，不改跨程序long/short排序、E protected_R、canonical成本、RAM/disk/CPU/pressure门、registry、CPU rebinder或FrameGuard。B one-shot<=12GiB例外包装gate.original_choose并从fallback调用当前aging.original，因此两者可以组合；无同时生产安装。

## Main-only接口

```python
pref = Preference(aging.original, engine, expected_pins, root=R)
proof = pref.install(aging, owner_assert)
# Save pref in Main's own activation marker. Only aging.original is swapped.
# proof contains wrapper/token runtime objects: serialize only status,
# source_sha256, captured_original_path, captured_original_sha256 for ACK.
pref.restore(owner_assert)
```

make_wrapper(original,engine,expected_pins,root=R)返回同B签名callable，可经其`__self__`保留Preference对象；显式Preference API更易审计。restore仅当前aging.original仍is安装的精确wrapper时恢复captured callable；若其它操作已换上新wrapper则拒绝覆盖。install/restore只允许Main线程，调用Main提供的owner_assert，并持有既有aging.lock。

未来安装前，Main须在q.additional_operational_overlays中提供`SAME_INPUT_DESIGN_P0_DEPENDENCY_PREFERENCE_V1`记录，`status=ACTIVE`、`source_sha256`为本模块发布SHA。captured B callable的source必须命中expected_pins，或命中已有ACTIVE operational record中的SHA；额外sourcepins同样逐个校验。Main仍负责发布/readback、实际owner birth/frame确认、保存对象和真实ACK。本组件不自行arm q或attach进程。

## CPU资格与范围

36项PASS。使用未改的generic B resource chooser与consistent完整门，隔离canonical spec/authority/headroom/history；实际E AgingChooser的pool过滤与fresh protected_R后验路径运行，但frame/advance输出为明确fixture。覆盖P0池外、跨输入/cell、spent/claim/INTENT/DONE/sealed、成本/limit变化、更贵不fit、原B三类HOLD、源码前中后漂移、long/short跨程序选择保持、E池外P0不能加入、E postcheck仍可拒绝、更换current callable后restore拒绝。

未修改现有生产owner/21pins、未登记、未派发、未启动模型。该资格不冒充当前活owner整条私有链已实际安装或真实资源余量PASS。此前参数模板39项测试未重复。
