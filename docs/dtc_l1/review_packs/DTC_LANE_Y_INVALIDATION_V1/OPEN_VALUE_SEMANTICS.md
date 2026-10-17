# 开放的数值语义问题

**VALUE_CORRECTNESS_UNPROVEN。CPU shadow-value oracle不是SASS architectural load值证明。** 参考模型只给事件输入附带整数token，不执行SASS、真实load/store payload、下层cache数据或ISA内存模型；生产common header也没有读值存储。

两组可核见证在`inputs/events.json`，IO/OO/sector均有观察记录：

|序列|输入token与期望|实际证据范围|
|---|---|---|
|SHADOW_STALE_OLD_CONSUMER|旧allocation四sector收到7；shadow memory改成9；E撤销lookup；旧消费者仍指向7|输出potential_stale；只说明保留旧身份允许这类token组合|
|SHADOW_DELAYED_OLD_RETURN|先接纳旧请求；shadow memory改9；E；保存旧identity的延迟返回token7|输出potential_stale；不证明真实下层会返回7，也不证明其ISA违法|

两者不是从trace推测真实数据。没有额外happens-before/scope和真实payload oracle，不能把7与9的不同自动判成一个已证实的架构错误，也不能把引用守恒当成架构正确。它们用于揭示需要另证的ordering/value条件。

本Lane另用生产IO/OO外部依赖API测试sidecar完成后同址映射仍可VALID_HIT，记录实际identity/counters。这只证明sidecar API不会撤销映射；没有模拟一次实际store/atomic。Lane V静态合同解释该API与真实分类/完成位置的关系：store dispatch完成不等同WRITE_ACK；PROXY_FENCE不是一般coherence；generation是allocation身份，不是数据版本。

仍需具备真实数据payload、明确期望值及支持域的litmus覆盖：L→S/ATOMIC→L、partial-byte/sector写、pending return跨write、cacheable与bypass混用、store ACK晚于sidecar退休、跨warp/SM/CTA/kernel同步及acquire/release/scopes。即使E后重新miss，返回新值也依赖下层可见性；无E时的旧映射可复用问题更不由最小K1解决。

当前未给这些问题制造期望架构值，未运行完整模拟。旧消费者及在途返回安全缺口保持FAIL_CLOSED；补证或新合同审查之后才能改变门禁，不能依靠terminal strict、credit平衡或旧A/T/U结果替代。
