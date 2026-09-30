# START HERE — AWMA R17R1 quality requalification

Date: 2026-09-30

Scientific parent:
`78874fbfd767ec1321d41a04e4c51589a3c07298`

This handoff continues R17 only because the first Lane-F run stopped at a **baseline quality qualification hole**, not because graph-search performance was negative.

Accepted R17 V1 facts:
- official normalized GloVe-100-angular input qualified;
- one device-resident CAGRA G64/IG128 index qualified;
- runtime `cuvs-cu12==26.8.1`, source `v26.08.01 @ 25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`;
- six preregistered Q1 MULTI_CTA points peaked at recall@10=0.930078;
- no formal timing/profiling/holdout was run.

New source audit:
- stable cuVS benchmark base config uses `NN_DESCENT` for CAGRA builds;
- stable benchmark base search grid includes `itopk={32,64,128,256,512}` and `search_width={1,2,4,8,16,32,64}`;
- the previous scientific index was built with the Python runtime default `IVF_PQ`, not the benchmark-base `NN_DESCENT`.

Therefore this round keeps recall@10 >=0.95 unchanged and repairs the strong-baseline qualification in two bounded stages:
1. extend search quality on the existing IVF_PQ index;
2. only if still needed, build one NN_DESCENT G64/IG128 index and repeat the bounded quality ladder.

Lane F / node109 is the only active lane.
Lane G and Lane E remain STOP.

Every CUDA/build/search/profile action uses:
`/data/c16/locks/c16_gpu_campaign.lock`.

Do not start another workload or candidate if this line stops early.
