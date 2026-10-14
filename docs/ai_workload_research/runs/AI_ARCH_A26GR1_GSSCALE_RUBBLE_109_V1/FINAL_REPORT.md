# A26GR1 GS-Scale real Rubble — bounded archive and native discovery closeout

Branch: `hrl/aiarch-a26gr1-gsscale-rubble-bounded-tar-109-v1`.
Base STOP: `e760f332ed41c609d3d19548f87d90b3f11357d8`; coordination: `b268bfa55390a67dad496d3ba71b31eac9aff2a2`.
The A27 review and GR1 proposal were read in full at the fixed coordinator; exact blobs/SHA are in RUN_IDENTITY.json. The user's explicit new approval overrides historical pending prose.
Author source remains `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`. All three complete software source trees were checked against fixed Git blobs.

## Actual gates

| Gate | Result | Scope |
|---|---|---|
| R0 | PASS | Compressed archive fits known current disk/reserve; official complete distribution metadata, fixed VCS entries and audited controller small transfer checked |
| R1 | PASS | Full official archive SHA/CRC and complete safety scan, safe extraction, real COLMAP bytes/consumed associations, exact author 4× preprocessing |
| R2 | PASS | Independent CPython3.10.12 environment, original old core versions/builds, CPUAdam actual numerical/thread canary |
| R3 | PASS, scoped | Actual full early train pipeline and basic metric APIs; three real windows including pre/post refine-stop reached continuously from zero |
| R4 | PASS — archived and published | First full packet push/fetch-back PASS; final closeout commit is also verified before STOP |

## Input and software identity

- Official archive: 9,773,995,561 bytes; SHA256 `85fd71d9d5b0b177d3e9493afb0d1d0f86b33e065b912443284b21df534daa6a`.
- Complete read-only scan: 3,365 members; 3,358 regular files; expanded logical bytes 9,801,136,458. Full gzip CRC checked to EOF and tar checksums/terminators verified. Traversal, duplicates, links, special/sparse and unqualified PAX were rejected. Extraction was bounded before writing.
- Official merged cameras/images/points3D SHA and controller→node full-file SHA agree. Cameras 1; images 1,678; points 1,694,315; 17,801,717 image features; all 9,523,399 consumed point→image track references checked.
- Six dangling image-feature forward IDs are preserved and disclosed. The frozen GS-Scale Parser constructs its used indices from reverse point tracks and does not consume those six forward entries. No input was deleted, reassigned or repaired. The over-strict added quaternion unit assertion was corrected to original reader semantics, without changing coefficients.
- Original 4× BICUBIC/imageio/Pillow function was executed with four CPU workers. All 1,678 output PNGs are 1152×864 RGB; four exact single-file source replays matched PNG bytes. Sorted-name train/test split is 1657/21 with test_every=83.
- Isolated core: Python3.10.12; Torch2.2.0+cu121; torchvision0.17.0+cu121; IPEX2.2.0; NumPy1.26.4; source gsplat1.5.0. Driver/SDK were not upgraded. CUDA12.6 compilation against the original cu121 stack was actually built and exercised.
- IPEX2.2.0 is officially yanked for security; the explicitly pinned original official distribution/SHA was retained in the isolated experiment. Three incorrect musllinux choices were replaced by same-version official manylinux wheels before qualification. No core version or math changed.
- CPUAdam original omp_set_num_threads(64) remains. OMP_THREAD_LIMIT=16 is an explicit software policy; real CPUAdam canary reported 17 running/18 resident threads, exact tested weight/moment error 0 and no CUDA initialization in that CPU test. It is not a claim of author64 tuning parity.
- The stock AlexNet weights are the unchanged author-default LPIPS evaluator component only, not an additional training workload. Its official SHA is locked. No global cache or old environment was modified.

## Real steps, numerical and quality scope

Original trainers execute frustum/gather/render/loss/backward/copies/CPU optimizer/state publication. Early optimized host and GPU-only each ran from the true SfM state to step205; basic real loss/output/parameter/active moments and PSNR/SSIM/LPIPS were finite.
The nominal max_steps=200000 and its LR/densification schedule stayed unchanged. External bounded stopping does not make a full-state checkpoint or flush all final pipeline gradients; no such checkpoint was resumed.
Two same-seed host trajectories really started at zero and reached step15200. First final N=6,672,954; corrected-observer final N=6,684,932. Densification trajectories are not bitwise identical across replays; treat differing states explicitly rather than imply a paired late speedup.
Long converged quality and matched time-to-quality are NOT_EVALUATED. Deferred Adam and GPU-only are not declared bitwise equivalent. Early normal steps are not paper Rubble PSNR convergence.

## Actual measurements and remaining service evidence

Early whole-cycle means for 100 actual samples: optimized host 38.439 ms; same input/camera-sequence GPU-only 29.272 ms; original diagnostic replay 41.380 ms. Same early N and actual camera order were checked, but the optimizer algorithm differs; no hardware speedup is inferred.
The original diagnostic observer conflated some H2D copy_ host calls with D2H. Its raw remains archived, and its directional breakdown is disqualified. A corrected source-line observer was verified by another real continuous trajectory within the original cumulative GPU budget.
Corrected windows use first 50 steps for diagnostics and the second 50 for the original train-body branch. Their different cameras/observer cost prohibit interpreting their difference as exact observer overhead or paired speedup.

| Real window (half-open) | N in corrected window | Original-body samples/mean | Diagnostic samples/mean | Blocking D2H + sync + join union mean |
|---|---:|---:|---:|---:|
| 100-200 | 1,694,315 | 50 / 39.268 ms | 50 / 47.172 ms | 7.834 ms |
| 14500-14600 | 6,476,865 | 50 / 132.480 ms | 50 / 186.431 ms | 30.871 ms |
| 15100-15200 | 6,684,932 | 50 / 133.810 ms | 50 / 147.425 ms | 32.128 ms |

CPU Adam and CPU parameter-forwarding Adam, ID/gradient/metadata D2H host blocking calls, H2D host enqueue, GPU event spans and synchronize/join are separately labeled with source lines. Per-call means differ from per-step sums; overlapping host intervals use unions. H2D enqueue is not a standalone transfer service time. CUDA spans include launch gaps and are not summed with unmatched host time.
**SCOPED_EXPOSED_HOST_WAIT_CANDIDATE_UNDER_OMP16**: nonzero complete-pipeline main-thread blocking intervals remain in two true late windows. This is observed service under this thread policy, not a demonstrated CPU bandwidth/PCIe/cache/SM bottleneck, physical hardware headroom, or a new mechanism.
CPU Adam exposed-tail attribution remains unqualified without reliable GPU completion clock alignment. Gaussian row indices across densification are not permanent identities; cross-step cache reuse was not measured. GPU-only late capacity/timing was not evaluated.

## Cumulative resource receipts and STOP

- A26G+GR1 network accounted upper bound: 14,473,965,675 bytes (13.480 GiB), including full controller download/relay and an uncertain interrupted Range charged by its full 32MiB bound. Cap25GiB.
- All new disk conservative total: 41.333 GiB, cap60GiB; current same-FS free 93.489 GiB, minimum64GiB. Raw/wheels remain private and are not in Git or copied to164.
- CPU preparation cumulative 11415.473s (3h10m15s), cap4h; requested idle after background completion explicitly excluded, never resetting prior work. Effective child running-thread peak 22 plus one supervisor <=24.
- Sampled task process-tree RSS peak 24.529 GiB, cap48GiB; sampled process VRAM peak 3638 MiB, cap14GiB. Torch allocated/reserved by arm and sampling limits are in BUDGET_CUMULATIVE.
- Shared GPU lock cumulative 3734.497s (62.24 min), cap120min. Nonblocking each acquisition; released after each stage. Compilation, first failed direct-wrapper startup and both legal continuous trajectories are counted.
- Ordinary packaging/runtime-observer problems were bounded, corrected and revalidated: metadata bounds/tags, CPython shared-library path, module-global cfg, copy-direction labels. Original source math was not edited. Every completed legal attempt remains identified.
- No full 200k training, other scene/seed campaign, NCU/NSYS/NVBit, simulator, SM-resource sweep, new Cache/atomic mechanism, driver/SDK upgrade or historical experiment was run.
- Old A26G STOP 21 files and old Lane M worktree HEADs/cleanliness were rechecked unchanged; no coordination merge.
- Final boundary: the approved scoped discovery is complete. Full quality convergence, late GPU-only comparison, stable Gaussian identities and physical causal attribution remain unqualified. No further GPU task or A26GR2 starts automatically.
- Only this independent branch is committed/pushed. Exact enclosing commit/tree/report blob and all submitted SHA are verified by remote fetch-back; self-referential hashes are not embedded. STOP after publication and await independent scientific review.

First packet verified commit `d9cd6bee253e8b1e2450ab9700eb4f1f0dd6a524`, tree `3171fecb9efdc7914c77f0b69773d05114b76aa4`; all 77 initial files matched. Final enclosing publication hashes are returned in the execution closeout.
