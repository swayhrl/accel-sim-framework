# Qwen BF16 Decode weight supply and Batch reuse diagnostic V3

Final status: **GPU_RESOURCE_DEFERRED / STOP**. Scientific conclusion: **INCONCLUSIVE**.
V3 completed the identity audit,changed-policy implementation,CPU qualification and the single real admission attempt. It did not obtain a legal model-execution window. Worker/model/warmup/formal counts are all0; deltaA00,deltaA01,deltaB2 and R remain null.

## Actual blocking process and resource decision

One CPU-only metadata audit inspected the three historical PIDs and only their necessary parent/service ancestry. It read PID,PPID,UID,comm,exe link,start time,cgroup and package/service ownership metadata,not private environment,command-line arguments or other-project data. The later real snapshot rechecked current start/UID/parent/service fingerprints,so the decision did not rely on a historical PID number alone.

| PID | Current identity | NVML category / memory | Classification and decision |
|---|---|---|---|
|3246996|UID1004,PPID1,comm python,exe /usr/bin/python3.12; ordinary user session-84262.scope;start ticks431862775|compute /423624704bytes|Ordinary user GPU-compute process,not a verified desktop service; forbidden. Specific task/project was not inspected.|
|1760|UID120,Xorg;GDM-session ancestry to root-owned active gdm.service MainPID1623|graphics /10248192bytes|Desktop-service identity verified via independent service/parent proof; activity qualification still pending.|
|2035|UID120,gnome-shell;GDM-session ancestry to the same root-owned service|graphics /6758400bytes|Desktop-service identity verified; activity qualification still pending.|

The Python process started at2026-11-03 16:48:51.75 Asia/Shanghai. Its current fingerprint still matched at admission. Xorg/GNOME exe symlinks were permission-denied; that exact gap is retained rather than inventing executable paths. Independent evidence was the active gdm.service MainPID1623,root UID,cgroup,display-session ancestry and unchanged start/parent identities. See CPU_PROCESS_IDENTITIES.json,DESKTOP_SERVICE_EVIDENCE.json,PROCESS_CLASSIFICATION.json and raw/ADMISSION.json.

The single nonblocking lock succeeded. The real pre-model NVML snapshot found **unqualified external PID3246996**. Combined external memory was440631296bytes (420.21875MiB),below512MiB,but low memory cannot substitute for desktop identity. A Python interpreter in an ordinary login session is not qualified simply because its GPU use might be idle.

The process-identity gate therefore stopped **before activity sampling and before spawning any worker/model**. Activity samples=0; no low-activity claim is made. There was no reason to wait or sample for an already-forbidden process to become idle. Final observation again found the same external set and no own GPU context. The lock was released/closed and NVML shut down after0.022019906seconds of held wall time. No retry,signal,suspension,priority change or other-process interference occurred.

No environment was admitted as QUALIFIED_DESKTOP_CO_RESIDENT. Consequently there is no DESKTOP_CO_RESIDENT_NATIVE_OBSERVATION performance result. This is a resource-identity STOP,not a numeric failure,a scientific negative or a lock conflict.

## V2 authority,identity reuse and isolation

Fetched V2 matches commit190352cb9fdb8b1db844f0388aa95876337c1436 and tree06e9fb7638dc571b230407a49432d53fd01f7b9d. V3 uses an independent branch/worktree and dedicated output,private inputs,tests,cache/log roots and receipts. Actual Goal start is2026-11-04 16:47:26 Asia/Shanghai (epoch1793782046). V1/V2 remain STOP and their historical raw,contracts,receipts,tools and caches were not changed.

All12 required model/tokenizer/config/license files matched V2's recorded inode,size,mtime_ns and ctime_ns. Their accepted V2 full-SHA identities were reused on that explicit ordinary-filesystem change-detection basis; **new full-model hash bytes=0**,not a new streaming-SHA claim. V3 independently rechecked required software/source/cache-interface hashes,package versions,A00/A01 original512-token canonical digests and historical-reference SHA. No retokenization,prompt replacement,weight/data download,dependency install or literature rescan was needed.

## Explicit resource changes versus unchanged science

V3 intentionally changes two resource/observation contracts,not model precision or numerical acceptance:

1. V2 rejected every external GPU process. V3 permits only independently verified desktop-service identities with unchanged live ancestry/start fingerprints,combined external memory<=512MiB and three fixed read-only activity samples within5seconds,each GPU utilization<=5%. Unknown/plain-user compute remains forbidden,even if memory use is small. During execution,new or changed unqualified PIDs,resource excess,observed desktopSM utilization>5% or unavailable required activity attribution stop the own task. There is no desktop-name-only or compute-list exemption.
2. GPU held budget increases720to1500seconds;Goal budget2700to3600seconds. Own VRAM15400MiB,RSS16GiB,new disk3GiB,one owner and one nonblocking lock attempt remain fixed. Qualified co-resident results would be labelled as such,never as fully exclusive measurements.

All model/input/numeric/point/order/timing scientific fields retain canonical SHA2568571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397. Model is Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1,BF16,TP1,no quantization. Intended engine remains VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttention,UnquantizedLinear,544/1088/2 capacity.

P1-P6,A00/A01,2warmups/5formals per point,interleaved order,exact token/length comparisons,finite logprobs,atol0.05/rtol0.01 and A00/output32 historical reference are unchanged. CUDA timing remains pre-sync,event start,complete generate,event stop,post-sync;host boundaries stay separate. The first planned warmup now explicitly enforces the already-required compiled/Graph identity using its existing recorded observations;no extra GPU point or weaker fallback is added. Live backend/Graph identity was not exercised this round.

## Engineering qualification

Final **37 CPU tests PASS**:23 inherited snapshot/lifecycle cases plus14 desktop-policy cases. Coverage includes typed memory sentinels,PID reuse and service restart,ancestry permission gaps,ordinary user compute,external memory cap,three low-activity samples,high/missing activity,bounded sampling time,new unknown compute,runtime external activity/gaps,resource/shutdown/unlock error paths and unchanged worker timing/numeric statements.

One inherited CPU fixture originally assumed its second snapshot followed worker launch. V3 correctly inserts admission-activity snapshots,so that fixture's artificial disk overflow occurred before launch. It was repaired to trigger after simulated spawn,without relaxing enforcement. The first failure is retained;the final complete test log passes. A controller script-transport parse failure before node execution also caused no node action or GPU attempt. No ordinary engineering issue was split into another Goal.

All successful mock model/formal outcomes remain only in ignored private CPU fixtures. They are not real samples. Formal persistence is header-only;no artificial GPU result is manufactured.

## Analysis and scientific limits

H1 weight supply,H2 compute/scheduling and H3 execution-identity alternatives remain untested by model timing. The observed failure concerns resource identity,not a demonstrated model/backend mismatch. There are no medians,MADs,paired B1/B2 numeric outputs,Graph observations or legal six-point contrasts.

Independent arithmetic on the inherited tensor manifest reconfirms6,171,394,048dense BF16 bytes and31 no-retention passes=191,313,215,488bytes. At nominal716.8GB/s the conditional ideal is266.899ms. This remains a structural model with the inherited full-scan,retention,tied-head and overhead assumptions,not measured DRAM traffic or achieved bandwidth. There is no observed request delta to compare.

The existing strong-software exclusion table is reused. Ordinary batch weight sharing already exists in software;no specific residual cost or new falsifiable hardware variable was measured. No candidate card,compression mechanism,Profiler,Simulator or RTL task is created.

## Required resource condition and final STOP

Recovery requires a resource-owner-arranged GPU window where **PID3246996's unqualified ordinary compute context is absent**,and no new unknown/ordinary compute context appears. The Python OS process need not be managed by this agent;this Goal neither requests nor performs a kill or GPU-state change. Any remaining desktop services still require the existing identity,external-memory and bounded low-activity conditions. A future GPU attempt requires explicit resource authorization;no further identical CPU-only audit Goal or background waiting/retry is proposed.

Actual resource observations are two complete real NVML snapshots with0ownMiB,external identity evidence and no NVML/PID observation gaps. Sampled own supervisor-tree RSS peaked37,994,496bytes. CPU tests recorded child high-water RSS;whole-Goal process-tree RSS was not continuously sampled,so no full-Goal measured-peak PASS is claimed. New disk/publication scope is recorded in receipts.

Model/data downloads,installs/upgrades,164 access,old asset/cache writes,NCU/NSYS/NVBit/Profiler,Simulator/RTL and interference with other processes are0. After Git publication and exact readback this Goal STOPs;no V4 or additional GPU attempt follows.
