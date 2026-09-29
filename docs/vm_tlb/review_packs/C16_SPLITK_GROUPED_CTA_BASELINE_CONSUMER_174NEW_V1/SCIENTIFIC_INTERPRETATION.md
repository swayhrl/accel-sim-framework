# 科学解释

GROUP_M16将split1 hit在K3072/K4096从63.56%/63.26%恢复到95.95%/95.95%，DRAM降至ROW的0.145/0.135，timing降至0.724/0.669。split8从GROUP仅获小幅改善。相同GROUP mapping下split1比split8快38.7%/30.9，hit近似相同且GEMM DRAM仅为split8的0.40/0.46。经典软件mapping已解决当前冻结点大部分split1 reuse问题，当前新split机制故事应关闭。
