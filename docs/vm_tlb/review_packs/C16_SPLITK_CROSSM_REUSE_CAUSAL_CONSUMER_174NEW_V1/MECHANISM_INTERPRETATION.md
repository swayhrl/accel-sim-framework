# 机制解释（准备态）

未来只比较同一patched binary下SHARED与PER_MTILE。K2560 split1应检验hit下降/DRAM与timing上升；K3072检验额外损失是否较小；split8检验约95.9%高hit是否依赖跨M地址共享。若不支持，直接降级机制解释，不追加replica扫描。
