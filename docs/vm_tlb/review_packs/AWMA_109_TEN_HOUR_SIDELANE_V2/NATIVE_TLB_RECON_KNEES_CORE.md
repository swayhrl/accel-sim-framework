# Candidate knees — reconnaissance only

A candidate is a >30% adjacent median change in the dependent-chain surface. It is not assigned to a TLB level.

- stride 4096: 512→1024, 52.0→158.0 cycles/load (ratio 3.04)
- stride 4096: 1024→2048, 158.0→244.0 cycles/load (ratio 1.54)
- stride 4096: 8192→16384, 302.5→425.5 cycles/load (ratio 1.41)
- stride 4096: 16384→32768, 425.5→645.0 cycles/load (ratio 1.52)
- stride 16384: 512→1024, 52.0→151.0 cycles/load (ratio 2.90)
- stride 16384: 1024→2048, 151.0→255.5 cycles/load (ratio 1.69)
- stride 16384: 8192→16384, 332.0→479.5 cycles/load (ratio 1.44)
- stride 65536: 512→1024, 52.0→168.0 cycles/load (ratio 3.23)
- stride 65536: 1024→2048, 168.0→220.5 cycles/load (ratio 1.31)
- stride 65536: 2048→4096, 220.5→295.0 cycles/load (ratio 1.34)
- stride 65536: 8192→16384, 307.5→434.0 cycles/load (ratio 1.41)
- stride 65536: 16384→32768, 434.0→623.5 cycles/load (ratio 1.44)
- stride 262144: 512→1024, 52.0→174.5 cycles/load (ratio 3.36)
- stride 262144: 1024→2048, 174.5→275.0 cycles/load (ratio 1.58)
- stride 262144: 8192→16384, 307.0→410.0 cycles/load (ratio 1.34)
- stride 2097152: 512→1024, 52.0→164.5 cycles/load (ratio 3.16)
- stride 2097152: 1024→2048, 164.5→220.5 cycles/load (ratio 1.34)

## Safe-capacity skips
- stride=262144, locations=32768, rc=3: SAFE_FOOTPRINT_EXCEEDED bytes=8589934592 thrash=0 free=16423714816
- stride=2097152, locations=4096, rc=3: SAFE_FOOTPRINT_EXCEEDED bytes=8589934592 thrash=0 free=16423714816
- stride=2097152, locations=8192, rc=3: SAFE_FOOTPRINT_EXCEEDED bytes=17179869184 thrash=0 free=16423714816
- stride=2097152, locations=16384, rc=3: SAFE_FOOTPRINT_EXCEEDED bytes=34359738368 thrash=0 free=16423714816
- stride=2097152, locations=32768, rc=3: SAFE_FOOTPRINT_EXCEEDED bytes=68719476736 thrash=0 free=16423714816
