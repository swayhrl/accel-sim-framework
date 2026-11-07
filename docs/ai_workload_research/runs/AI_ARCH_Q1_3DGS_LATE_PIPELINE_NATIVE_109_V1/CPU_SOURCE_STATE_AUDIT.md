# CPU source and checkpoint-state audit

This is a source review plus CPU fixture test, not qualification of a real GPU checkpoint. Original trainer and C++ SHA256 match the expected frozen authority. No historical source was modified. The original save at trainer lines 1324-1326 contains only step and splats.

A minimally invasive private AST extraction can preserve original arithmetic statement order while moving cross-step locals into a named state dictionary. Use PIPELINE_PREPARED after line 1293, before the next iteration's synchronize/thread launch at 1023-1031. The previous GPU thread is joined at 1075, but synchronize outstanding prepared H2D copies before serializing values. Do not execute a full-N optimizer flush merely to make checkpointing easier.

## Required state

Cross-step locals: next_step, is_densify, counter, valid_ids, valid_ids_cpu, valid_ids_cpu_prev, camtoworlds, Ks, pixels, image_ids, masks, height, width, opacities, colors0, colorsN.

Also save parameter data and CPU pending .grad; both optimizer families with names, moments, step and hyperparameters; scheduler states; every strategy-state key and its config; row order and Gaussian lineage; Python, NumPy, Torch CPU and owned CUDA RNG states; camera sampler state and source identities. Parameter .grad is not part of ordinary state_dict() and cannot be omitted. Restore optimizer parameter references against re-created named parameters.

Prepared opacity/SH leaf tensors must be saved as actual values with dtype/device/shape/stride/requires_grad. Lines 1257/1287 use pending gradients and deferred counters to predict the next GPU-visible values without committing CPU weights. Recomputing these leaves from CPU weights alone, rerunning prologue, or discarding pending gradients changes the training trajectory. results, info, transient optimizer aliases and transfer scratch buffers are not mathematical cross-step live-ins. Rebind progress/log wall clocks separately.

At this safe point GPU step t is complete, CPU gradients for t are pending, and camera t+1 is already loaded/prepared. Maintain an explicit credit ledger for rendered camera, applied CPU gradient, optimizer steps and counter ages. A splat-only state does not carry this pipeline phase.

## Loader replay without inventing cameras

Original loader is shuffle=True, four persistent workers, pin_memory=True. Installed RandomSampler consumes one main Torch RNG seed per epoch and uses a private generator for its permutation. Initial DataLoader construction separately draws the worker base seed; persistent epoch reset does not redraw it.

The isolated StatefulLoader materializes the original RandomSampler iterator at its original first-index dispatch point, records that full permutation, and separately counts batches actually delivered to training. Materializing the private-generator tail does not add main-RNG consumption. Prologue consumes two batches: one rendered and one prepared. Resume reproduces only recorded unconsumed indices; prefetched-but-undelivered deterministic samples can be regenerated, and the currently prepared GPU camera/pixels are separately checkpointed. A private generator reproduces the original worker base-seed draw without consuming checkpoint main RNG; later epochs again use the original main-seeded sampler.

Dataset.__getitem__ (colmap.py392-452) is deterministic when patch_size=None; random crop exists at 411-418 otherwise. image_id is Dataset item index, not parser index. Bind Dataset.indices and source names with a mapping digest and compare real returned camera/pixel hashes after restore. No generic claim is made for stochastic workers: Python/NumPy worker RNG streams are not captured, and stochastic transforms must be rejected unless separately qualified.

## C++ hidden state and drain boundary

All weight, first/second moments and int8 counter storage in cpu_adam.cpp is supplied as Tensor arguments. No persistent static/thread_local mathematical storage appears in that translation unit, header or pybind API. OpenMP policy and FTZ/DAZ are executing-thread environment: keep them consistent and record observed effective teams. Six operations request 64 OpenMP threads internally; affinity/OMP caps remain necessary.

update_counter increments N entries and resets U; adam_deferred_update indexes corrections by counter age, expected 0..15. Do not reset it at an ordinary checkpoint. The source's true terminal max_steps-1 branch forces a full-N deferred update. An artificial intermediate full-N flush is a different state from the ongoing pipeline. Preserve undrained checkpoint semantics and account separately for any explicitly defined final drain, including remaining credit and actual work.

## CPU verification and remaining qualification

Fourteen unittest cases PASS in 49.518s (52.444s subprocess wall), retaining the expected four-workers/two-helper-CPUs warning. Tests cover exact original-loader initial order and main RNG; three epochs; mid-epoch and cross-epoch restore; completed-epoch restore; batch1 and prologue cursor; mapping digest; invalid identity/permutation/cursor/RNG; deterministic-Dataset gate; four-worker shutdown. Fixtures are not scientific inputs. CUDA_VISIBLE_DEVICES was empty, pin_memory=False, affinity22/23; no CUDA or NVML API calls. Child ru_maxrss was 387520 KiB, not an aggregate Goal peak. Log: [LOADER_CPU_TEST.log](raw/LOADER_CPU_TEST.log).

GPU owner must still demonstrate real full-state save/reload, matching next camera and pending gradients, same-source continuous versus resumed trajectories under the frozen numerical contract, actual extension/runtime identity, and final-drain workload closure. This audit does not mark those checks PASS.
