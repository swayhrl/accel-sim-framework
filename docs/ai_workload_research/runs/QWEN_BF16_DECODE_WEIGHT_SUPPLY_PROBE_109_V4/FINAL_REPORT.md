# BF16 Decode weight supply and Batch reuse diagnostic V4

Final execution status: **GPU_RESOURCE_DEFERRED / STOP**.
Scientific conclusion: **INCONCLUSIVE**. Worker/model/warmup/formal counts are all0;no legal six-point results,deltaA00,deltaA01,deltaB2 or R were obtained.

## Window confirmation and actual admission

The user explicitly confirmed that the resource owner had approved the current109execution window. RESOURCE_WINDOW_STATUS.json records that confirmation before the only real lock attempt. The confirmation authorized the attempt;it did not waive the mandatory live-resource predicates.

The single nonblocking campaign-lock attempt succeeded. Actual RTX4080 UUID matched. Before any worker/model launch,NVML again listed:

|PID|Live category|GPU memory bytes|Decision|
|---|---|---:|---|
|3246996|compute|423624704|Ordinary user process,UID1004,comm python,PPID1,user login-session cgroup;no desktop-service qualification. Reject.|
|1760|graphics|10248192|Xorg desktop-service identity and GDM ancestry still match the V3 evidence;activity qualification not attempted.|
|2035|graphics|6758400|GNOME Shell desktop-service identity and GDM ancestry still match;activity qualification not attempted.|

The current PID/start/UID/parent/cgroup fingerprints were checked by the actual supervisor,not inferred from a historical PID's presence or absence. PID3246996 still matched start ticks431862775. Its earlier executable metadata is /usr/bin/python3.12;V4 did not inspect private arguments,environment,project data or the process's purpose. It remains an ordinary user GPU-compute context rather than a verified desktop service.

Combined external memory was440631296bytes (420.21875MiB),below512MiB. That does not override the ordinary-compute exclusion. The identity gate correctly stopped before bounded activity sampling;activity samples=0 and no low-activity claim is made.

Two actual resource snapshots were saved. Final observation found no own GPU context,and the lock was released/closed with NVML shutdown after **0.022193558seconds** held wall. No wait,retry,whitelist,signal,suspension,priority change or other-process intervention occurred. raw/ADMISSION.json retains the exact original receipt;RESOURCE_RECEIPT.json adds scope annotations.

This is an actual resource-qualification failure inside the confirmed window,not a new engineering defect,lock conflict,numeric failure or performance negative.

## Direct V3 reuse and isolation

Fetch matched V3 commit24250f101719044407eceed9c2523696dc30d9b2/tree4ceb8c04c9c27fd191bfd0a0c1d53c8a82142c8f. V4 is a separate worktree,branch,Goal time binding,output,private input/cache/log and tool prefix. V1,V2,V3 were read-only.

No runtime algorithm or admission policy was developed anew. Worker,persistence,snapshot/supervisor and desktop-policy source is byte-identical to V3 after only V4/V3 path normalization. Accepted37CPU cases pass after rebinding;syntax and immutable science identities also pass. There was no literature rescan or engineering redesign.

All12 required assets retain their accepted inode,size,mtime_ns,ctime_ns fingerprints. Their earlier fullSHA authority was reused;new full-model hash bytes=0,not a new full-stream SHA claim. Required software/source/cache-interface hashes,package versions,original A00/A01 canonical512-token identities and historical-reference SHA were reconfirmed. The revalidator reads accepted V3 private copies and writes only V4.

Copied CPU_PROCESS_IDENTITIES.json,PROCESS_CLASSIFICATION.json and DESKTOP_SERVICE_EVIDENCE.json are explicitly V3 provenance,not newly performed V4 system-wide audits. Live V4 ancestry/start/UID fingerprints are in the current resource snapshots. Prior Xorg/GNOME exe-read permission gaps remain disclosed;qualification uses the accepted independent GDM service proof plus matching live ancestry.

## Unchanged scientific and resource contracts

Scientific-field SHA remains **8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397**.

The planned model remains Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1,BF16,TP1,no quantization. One strong VLLM_COMPILE/inductor/FULL_AND_PIECEWISE engine,FlashAttention,UnquantizedLinear and capacity544/1088/2 are required. No eager or weaker fallback is allowed.

Original A00/A01,P1-P6,B1/B2,output1/32,interleaved order,2warmups/5formals per point,sampling,exact length/token pairing,finite logprobs,atol0.05/rtol0.01 and A00/output32 historical checks are unchanged. CUDA timing remains pre-sync,event start,complete generate,event stop,post-sync;host boundaries remain separate. First planned warmup would perform accepted actual backend/Graph/numeric qualification. None was reached.

V3 desktop rules and budgets are unchanged:independent desktop identity plus live fingerprints,combinedexternalVRAM<=512MiB,three low-activity samples within5seconds at<=5percent,continued monitoring and fail-closed unknown/ordinarycompute rejection;GPU1500seconds,Goal3600seconds,own15400MiB,RSS16GiB,newdisk3GiB,one GPUowner and one nonblocking lock attempt.

No environment was admitted as QUALIFIED_DESKTOP_CO_RESIDENT and there is no DESKTOP_CO_RESIDENT_NATIVE_OBSERVATION result.

## Scientific analysis

FORMAL_SAMPLES.tsv is header-only. NUMERIC_AND_IDENTITY.json explicitly records NOT_MEASURED;there is no numericPASS or actual compiled/Graph reproduction claim. Point medians/MAD and all four requested contrasts remain null.

H1 weight supply and H2 compute/scheduling cannot be assessed without current legal request timings. H3 is not a demonstrated model/backend mismatch here;execution never reached the model because resource identity failed. Old resourceSTOPs are not performance samples or evidence against either hypothesis.

Independent arithmetic over the inherited tensor manifest reconfirms6,171,394,048denseBF16bytes;31no-retention passes imply191,313,215,488bytes and266.899ms at nominal716.8GB/s. These are conditional structural assumptions,not measured DRAM bytes,achieved bandwidth or an unconditional bound on a signed request difference. No actual delta exists for comparison.

The V1/V2/V3 strong-software exclusion table is reused. Ordinary batch sharing is existing software capability. No specific unexplained residual or new hardware variable was observed;no candidate card or new experiment is proposed.

## Distinct V1-V4 outcomes and resource condition

- V1:pre-model NVML Python API defect;0formal.
- V2:API repaired;strict no-external-process policy rejected three actual PIDs;0formal.
- V3:desktop service identities established and co-residence policy added,but ordinary user Python compute still forbidden;0formal.
- V4:current resource-owner-window confirmation obtained and accepted runner reused;liveNVML still found that ordinary compute context,so the unchanged policy stopped;0formal.

These are different operational outcomes,not four performance negatives. V1_V2_V3_V4_COMPARISON.json separates them.

The remaining condition is concrete:an approved window in which the external ordinary/unknown compute context is actually absent from liveNVML. Any remaining desktops must still pass their identity,memory and bounded activity rules. This Goal will not manage the other process,repeat aCPU-onlyaudit,wait in the background,retry the lock or create V5.

Own NVML use was0MiB in both actual snapshots;sampled supervisor-tree RSS peaked37,961,728bytes. CPU tests record child high-water RSS;entire-Goal process-tree RSS was not continuously sampled,so no full-Goal measuredpeakPASS is claimed. Monitoring scope and disk counts are in receipts.

Downloads,dependency changes,164 access,old assets/caches writes,Profiler/NCU/NSYS/NVBit,simulator/RTL and intervention in otherGPUtasks are0. Publication includes exact commit/tree/blob fetch-back and clean verification,thenSTOP.

Publication engineering note: SSH public-key authentication was unavailable. Existing gh credentials were reused with a per-command HTTPS transport override; no keys,dependencies or persistent Git configuration changed. One GitHub500 receive error was resolved by one nonforce retry after checking remote state. This affected only publication,not the single GPU attempt or scientific result. PUBLICATION_TRANSPORT_RECOVERY.json records the bounded recovery.
