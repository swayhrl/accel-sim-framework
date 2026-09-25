# Validation ledger

Status: `ALL_REGISTERED_ROWS_TERMINAL_AND_STRICT_PASS`.

R1 is complete: all twelve BICG rows natural-exited and strict-PASSed.  The
R3/R4 work below is intentionally listed row by row so an in-progress process
is never mistaken for accepted evidence.

| Phase | Workload | Mode | Point | Immutable UUID | Status | cycles | Evidence use |
|---|---|---|---|---|---|---:|---|
| R1 | BICG | IO | A | `17f8045e-c206-49de-95c6-15bf04a31d69` | PASS | 94,719,567 | accepted |
| R1 | BICG | OO | A | `a5473bd5-0871-4455-96c8-2d0087d476e8` | PASS | 47,588,121 | accepted |
| R1 | BICG | IO | B | `eba6d345-5a24-447b-87b1-1f2067042dd3` | PASS | 95,999,800 | accepted |
| R1 | BICG | OO | B | `c98b07f1-d896-4da6-bf9d-e9c8b775192f` | PASS | 48,487,452 | accepted |
| R1 | BICG | IO | C | `aa059e1a-a270-4764-bf4f-7f361a80ce3c` | PASS | 93,942,704 | accepted |
| R1 | BICG | OO | C | `b3eb2c89-5857-4138-8b53-50da953d95df` | PASS | 47,231,655 | accepted |
| R1 | BICG | IO | D | `6e5a496d-10b3-4468-903b-826590285e1d` | PASS | 95,999,800 | accepted |
| R1 | BICG | OO | D | `68d7beb1-587d-4064-8391-0e1b25d6cc5f` | PASS | 46,926,203 | accepted |
| R1 | BICG | IO | E | `ba9a1148-c994-419d-94b1-a258d59ddeb7` | PASS | 50,713,356 | accepted |
| R1 | BICG | OO | E | `7eb34930-7335-4263-a8dd-03e219691b04` | PASS | 29,933,876 | accepted |
| R1 | BICG | IO | F | `6cae8e74-9ff8-422b-84e4-8d49638a69e3` | PASS | 50,091,053 | accepted |
| R1 | BICG | OO | F | `b3c56644-2675-4bcd-8e0f-6c96f94ad235` | PASS | 29,411,883 | accepted |
| R4 | BICG | OO | F + 20MiB L2 | `d79538e9-afaa-487c-9bf2-cddb154352f0` | PASS | 22,204,820 | accepted R4 OO row |
| R4 | BICG | IO | F + 20MiB L2 | `94815fb0-08e2-4363-80af-1d8105fa8fd2` | PASS | 47,347,123 | accepted R4 IO row |
| R3 | GESUMMV | IO | F | `878fcea9-4e1e-4fb9-8202-9dfd536e83ce` | PASS | 103,536,854 | accepted R3 F/IO row |
| R3 | GESUMMV | OO | F | `51eab426-3980-4d5e-b0f2-10e8e24acffb` | PASS | 77,454,520 | accepted R3 F/OO row |
| R3 | GESUMMV | IO | E | `95e5acc8-f72e-4dc2-91fb-2e4b84425712` | PASS | 107,119,606 | accepted R3 E/IO row |
| R3 | GESUMMV | OO | E | `cb1f0372-1157-4d68-a79b-c8afd0758196` | PASS | 79,382,011 | accepted R3 E/OO row |

The R4 ceiling pair is now terminal and strict-PASS.  It is 5.48% faster than
F/IO and 24.50% faster than F/OO, respectively.  This is a bounded paired
ceiling result, not a capacity sweep or a universal L2-capacity attribution.
Both R3/F rows and both gate-authorized R3/E rows are terminal and
strict-PASS.  No further simulation is registered or required by this plan.
