# EP-L2 calibrated baseline decision template

Status: template only. Lane D must not fill the decision or mark
`BASELINE-DECISION` complete.

| Decision case | Required evidence | Outcome / owner review |
| --- | --- | --- |
| Retain D256 | D512 pressure/speed sensitivity; lower-path movement; negative controls; 256 hardware-cost rationale | Pending combined review |
| Promote D512 | provenance-compatible D512 mirror; descriptor pressure movement; D512 hardware cost; cross-workload response; no hidden config delta | Pending combined review |
| Retain L1 BASE | D256/D512 × META-HR/BANK-HR speed and lower-pressure movement show no material causal L1 limitation | Pending combined review |
| Recalibrate L1 | headroom sensitivity/decomposition shows a hardware-plausible L1 resource materially changes results or unmasks L2/lower pressure | Pending combined review |

The decision record must include cycles, descriptor and Line-MSHR pressure,
L1 retries, WAD/payload/bank events, lower traffic/scheduler/BW, temporal
bursts/imbalance, hardware plausibility, provenance, and negative controls.
No occupancy or retry count alone establishes causality.
