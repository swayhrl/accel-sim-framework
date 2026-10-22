CFD和DWT两个已接受r5 F端点，每个物理阶段的真实TagFAIL、relieve、detach都为0。covered目标set最多RESERVED分别4和3；新Tag需求子集最多均3。因此本次未到达all16 RESERVED的必要触发点，而不是没有RO。

CFD的RO及eligible集中在后两阶段：UID4/5分别产生3,036/48,642个observer RO admit事件；eligible head-cycle为6,077/98,765。UID5还包含全部66,779次MISS且reserved=invalid=0，以及234次新Tag+certifiedRO+eligible真实联合；仍无实际TagFAIL。前3阶段maxReserved0且无RO admit/eligible。

DWT的全部9,965个observer RO admit与20,185次eligible暴露发生UID1物理阶段（maxReserved2）；后续UID2/5/8仍有MISS和同line HIT_RESERVED，但eligible0、maxReserved3。其它UID3/4/6/7/9/10的covered全HIT、maxReserved0。它们反映事件发生时段，不说明请求或victim由哪个kernel因果生成。

满Tag不等于不可替换：CFD66,779、DWT361,550次MISS暴露已有16个非RESERVED且非INVALID的way，仍按冻结规则可替换。DWT7,250次HIT_RESERVED也不是all16 RESERVED。所有数值是head-cycle/way暴露或显式RO事件计数，不能改称独立请求。

TVDskip（CFD218,239/DWT335,584）仍须NA：这些调用实际先做过Tagprobe，本次handled绕过普通RO/FT relief；WAIT后可能回普通路径，不能称没有probe、没有压力或永远不需Tag。Vector/Conv的r5同set与阶段联合仍缺，不能用其旧r4零触发回填。原main61配对与当前F诊断分开，尚不能归因旧F收益给未发生的Tag-detach；本阶段仅2/4。
