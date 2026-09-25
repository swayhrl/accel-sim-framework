# Passive last-result forwarding V2R1

Status: **COMPLETE / PASSIVE_FORWARDING_OPPORTUNITY_ALREADY_PRELAUNCHED**

V2R1 restores the frozen V1 resident-access prelaunch traversal and keeps the
one-entry instruction-local forwarding rule unchanged. All correctness gates
and the real full-pipeline zero-opportunity exact gate pass.

| target | OFF cycles | V2R1 cycles | speedup | forward hits | physical lookup delta |
|---|---:|---:|---:|---:|---:|
| T0 | 527,896 | 518,842 | 1.715111% | 2,722,464 | 914 (0.004304%) |
| T1 | 665,802 | 656,991 | 1.323366% | 6,629,952 | 2,287 (0.003753%) |
| T2 | 93,079 | 92,155 | 0.992705% | 132,544 | -97 (-0.017662%) |
| SPLITKV | 73,923 | 73,783 | 0.189386% | 218,862 | -1,483 (-0.074249%) |
| COMBINE | 10,480 | 10,480 | 0.000000% | 1,016 | 0 (0.000000%) |
| A1 | 114,123 | 116,693 | -2.251956% | 116,032 | 33 (0.006044%) |
| A2 | 117,698 | 115,860 | 1.561624% | 116,032 | -16 (-0.002931%) |

The decisive accounting result is that every one of the
9,936,902 forwarding hits occurred after real
resident-prelaunch work had already been admitted. The number of hits is
therefore not physical-service suppression. Total lookup-request changes are
only -1,483 to +2,287 requests across targets (OFF-minus-V2R1 convention), and
the largest absolute fraction is 0.074249%. Some points
increase physical requests. This supports the preregistered negative outcome:
the passive opportunity observed at the head is already prelaunched by frozen
V1.

Cycle responses are retained as development evidence but are not attributed
to translation-service elimination. T0/T1 improve by 1.715%/1.323%; A1
regresses by 2.252%; these responses accompany scheduling/admission changes
while physical lookup service is essentially conserved. The stage therefore
does not advance to independent holdout.

A2 is 117,698 cycles OFF, 112,145 cycles in mixed V2 (diagnostic only), and
115,860 cycles in V2R1. V2R1 retains 116,032 forward hits but changes lookup
requests from 545,916 to 545,932 and reduces admissions versus OFF rather than
reintroducing the old proactive-owner +1.1M amplification. The mixed-V2
+4.718% result is not passive-only evidence.

The future holdout preregistration `d450b2a06a0af18960d81b0ccbb46d047fe6cbae` remains unchanged. Neither
`STR_e0922aa2a506` nor `STR_48b98b28a393` was captured or run.
