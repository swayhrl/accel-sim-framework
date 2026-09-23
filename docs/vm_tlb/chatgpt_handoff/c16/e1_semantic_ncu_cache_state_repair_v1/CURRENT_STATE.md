# Current State — E1 Semantic NCU Cache-State Repair

## Accepted upstream

Clean E1 producer:
`8988d6108ff8bdca180a14cec2fe769df45b09f1`

Independent clean consumer:
`59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Semantic NCU V1 producer:
`9ad003fff0d42b544d3a703eca4846364c13ccb6`

Consumer hardening:
`hrl/c16-e1-semantic-ncu-consumer-hardening-v1@396233ca250c20be834aa0c50d2504e6017953bc`

## Audit result

V1 selector and raw arithmetic are valid.

Independent raw-CSV recomputation confirms:

| metric | M1 AWQ/RAW | M256 AWQ/RAW |
|---|---:|---:|
| l1tex__t_bytes.sum | 0.1737193764 | 3.3837209302 |
| lts__t_bytes.sum | 0.3038159794 | 3.0267706296 |
| dram__bytes.sum | 0.2587944202 | 1.1065566466 |

V1 raw CSV also records seven replay passes for every selected kernel.

The V1 session command uses default kernel replay/cache behavior and does not set `--cache-control none`.

Therefore V1 traffic is retained as a cold/isolated kernel-replay diagnostic, not final native/warmed semantic-module traffic.

## Current action

Run the bounded V2 cache-state repair on node109 using the design and Goal in this directory.

174-new should remain stopped until V2 producer evidence exists.

After V2:
- resume the hardened 174 consumer;
- require direct verification from producer raw NCU exports/session evidence;
- do not consume producer-normalized traffic TSV as sole authority.
