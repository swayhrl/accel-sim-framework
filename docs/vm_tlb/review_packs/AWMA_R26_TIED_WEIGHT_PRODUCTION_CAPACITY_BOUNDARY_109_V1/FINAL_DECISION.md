# Final decision

`R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED`

C1 confirms B70 PASS and B71 OOM; S2 confirms B71 PASS and B72 OOM. The same B71 witness is C1 OOM 3/3 and S2 five-complete-step PASS 3/3. Both OOM endpoints occur in backbone/compact-lookup backward; C1 fails on the third repeated B71 step after its prior full-gradient allocator history.

At B70, TARGET_REGION and COMPLETE_TRAIN_STEP are both MIXED in all three groups. Whole-step peak is dominated by the common backbone path, so R25's local target-memory reduction does not appear as a lower determining peak here. Capacity and timing are separate: this is a one-batch physical-capacity extension for repeated identical content, not convergence, all-parameter training, or unified speedup.
