# T2 HARD acceptance

| requirement | evidence | status |
| --- | --- | --- |
| same immutable payload | all modes: `TRACE_BUNDLE_ID=ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`, `kernelslist.g` SHA-256 `6d277910149236df31f19532ac68e09415416b603e44094316f95028bdf9ba3a` | PASS |
| repair-bound platform | 80 SM, global DTC lower cap 10240, ratio zero; Core `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`; runtime Framework `dc7836c484544b78d143837bbbb40ecbabb15aee`; binary SHA-256 `3e71cb73e7769be43fc4e7c95c59dba6d50540e3827a38a46e4016cb2877dc27` | PASS |
| Base terminal/strict parse | `50,303,549` cycles; `158,601,216` instructions; PIB admit/retire `3,145,984/3,145,984`; lower acquire/release `19,175,277/19,175,277`; final PIB/lower `0/0` | PASS |
| IO terminal/strict parse | `9,324,397` cycles; `158,601,216` instructions; lower created/issued/responses `17,823,985/17,823,985/17,823,985`; dependencies `18,350,080/18,350,080`; final inflight/PIB/lower `0/0/0` | PASS |
| OO terminal/strict parse | `8,764,792` cycles; `158,601,216` instructions; lower created/issued/responses `17,827,090/17,827,090/17,827,090`; dependencies `18,350,080/18,350,080`; final inflight/PIB/lower/active refs `0/0/0/0` | PASS |
| trace frontend/path | each argv supplies the immutable `kernelslist.g`; stdout records ordered `.traceg` processing/header loading, with no PTX application command | PASS |
| final failure scan | no fatal/assertion/deadlock/stale-fill/duplicate-lower/unclassified trace failure signature in any mode | PASS |
| repair invalidation | pre-repair Core `12097864...` T2 remains a diagnostic anchor only; this triplet was replayed naturally under the repaired Core with no artifact relabelling | PASS |

T2 therefore re-admits T3 (GESUMMV contrasting qualification) under the active
Core.  It does not by itself close M5.0BT or Q1.  The separate lower-create
repair qualification still requires the live ATAX recovery triplet to close
before repaired MVT and GESUMMV dispatch.
