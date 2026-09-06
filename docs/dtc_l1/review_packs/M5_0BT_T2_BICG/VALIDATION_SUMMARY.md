# T2 HARD acceptance

| requirement | evidence | status |
| --- | --- | --- |
| same immutable payload | all modes: `TRACE_BUNDLE_ID=ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`, `kernelslist.g` SHA-256 `6d277910149236df31f19532ac68e09415416b603e44094316f95028bdf9ba3a` | PASS |
| frozen platform | 80 SM, global DTC lower cap 10240, ratio zero; Core `120978646e4c8bae2707ddfc6b31512a4a0c76c8`; runtime Framework `554743644bfd3fc28fac13bc1b78fc9f9fa6ba4f`; clean binary SHA-256 `9b51000ecb591785223e3a59ab90df896ef8996284c3d2b1e8832090635944c2` | PASS |
| Base terminal/strict parse | `50,303,549` cycles; `158,601,216` instructions; PIB admit/retire `3,145,984/3,145,984`; lower acquire/release `19,175,277/19,175,277`; final PIB/lower `0/0` | PASS |
| IO terminal/strict parse | `9,324,397` cycles; `158,601,216` instructions; lower created/issued/responses `17,823,985/17,823,985/17,823,985`; dependencies `18,350,080/18,350,080`; final inflight/PIB/lower `0/0/0` | PASS |
| OO terminal/strict parse | `8,764,792` cycles; `158,601,216` instructions; lower created/issued/responses `17,827,090/17,827,090/17,827,090`; dependencies `18,350,080/18,350,080`; final inflight/PIB/lower/active refs `0/0/0/0` | PASS |
| trace frontend/path | each argv supplies the immutable `kernelslist.g`; stdout records ordered `.traceg` processing/header loading, with no PTX application command | PASS |
| final failure scan | no fatal/assertion/deadlock/stale-fill/duplicate-lower/unclassified trace failure signature in any mode | PASS |
| provenance correction | legacy IO/OO metadata typo is retained; new strict summaries with runtime SHA `554743...6ba4f` parse the same output logs and preserve all simulation artifacts | PASS |

T2 therefore admits T3 (GESUMMV contrasting qualification). It does not by
itself close M5.0BT or Q1.
