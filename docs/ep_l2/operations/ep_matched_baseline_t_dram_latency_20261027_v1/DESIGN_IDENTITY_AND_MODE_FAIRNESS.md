# 设计、有效延迟与正式模式公平性

固定64slice/32channel/32set×8way/128B、SM/L1/ICNT/DRAM时钟1132:1132:1132:850MHz、非simpleDRAM、ROP160和原队列/Bank timing。六点同一Core c67b332db703f09571ba6628222c77d71440e141与ELF ad4421b441d1f8efef4c956381ede5e6fd7389147d26960931e202e0a38e4b07；五个新启动+精确旧D参考。全282有效选项按正式模式和延迟逐项比对，输入trace composite 138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940。

S使用历史正式FT1基线，关闭TVD clean/dirty、M和T，payload_mode2/静态s64=0保持。F−T与F均正式FT2+W/V/M，只有T=0/1。不是把错误static_s64路径当S。详见MODE_FAIRNESS_AUDIT.md的文件函数行号和MODE_OPTION_DELTA.json。

物理资源均1024Resident+128Bypass+16WB=1168slots、4×292bank，1op/bank/cycle、descriptor512、WAD128、MSHR128/merge1。FT1静态Tagindex→Resident映射在256个逻辑Tag下只使用前256个固定Resident位置；FT2可按正式角色分配资源，TVD128。此差异属于历史正式机制语义，不伪称每角色可用额度相等；本轮只能比较给定正式资源模型，不能据此证明等面积硅实现。只缩Tag逻辑组织而保持Payload物理资源，不称实际SRAM面积减少。

SOURCE_KEEP。不改accepted EP-MAIN/Core/旧57次台账/前Goal接受点，不混入历史1093/9243/d010谱系。实验授权固定五个新精确cohort，NativeQ/新预算/consume-beforefork/soleentry/DONE+PIDmaps+argv/env+strace实际读取闭合。60条件因L0非30不成立；冻结后未改科学spec。
