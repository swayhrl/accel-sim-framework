# Field semantics

`observed` is once per exact frontend preview cycle; `any_blocked` is at most once per observed cycle. Reason bits are independently evaluated and may overlap, so they are not a partition. Useful admit is recorded only after actual admission; useful response enqueue only at the actual L2-to-ICNT retirement boundary. Resident occupied/free samples are production resident state at the B0 sampling point. Windows are exact 5K-cycle, 64-slice groups; parser fails closed on incomplete groups.
