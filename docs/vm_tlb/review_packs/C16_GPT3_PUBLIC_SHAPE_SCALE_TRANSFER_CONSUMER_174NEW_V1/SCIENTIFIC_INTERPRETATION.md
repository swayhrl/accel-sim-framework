# 科学解释

独立raw重算确认两处明确方向翻转：EXPAND_M1从旧Qwen的-41.30%变为24.10%；EXPAND_M256从旧Qwenwarm +30.00%/disturbed +26.93%变为-71.01%/-73.63%。前者与split1 grid从148增至384一致，后者同时伴随新M256 warm DRAM中split1显著高于split8，但这些只是联合一致性，不是唯一L2因果。

CONTRACT_M1仍退化，但由旧Qwen -413.32%缩小到-63.92%，属于幅度明显缩小而非问题消失。CONTRACT_M256为warm -36.02%、disturbed -35.06%。

qweight从0.506×L2变为4.5×L2后，EXPAND_M256 interaction为2.62个百分点，CONTRACT_M256为-0.97个百分点；与旧Qwen +3.07/+5.34个百分点相比呈混合变化，而非统一增强。W/E DRAM和timing共同表明状态仍有影响，但不能唯一归因L2。

W4仅是GPT-3公开尺寸映射到AutoAWQ内核的机制代理，FP16 Dense只是大shape anchor。现有强crossover值得建议一组后续paired机制研究：旧Qwen UP_M256与GPT-3 proxy EXPAND_M256；本consumer未启动SASS或Accel-Sim。
