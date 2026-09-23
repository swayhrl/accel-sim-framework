# Observable identity

Actual M0/M1 SASS uses `CS2R` at PC `0x240` for start and PC `0x10b0` for end. The dependent `LDG.E` chain lies between them. Every captured warp has two unambiguous pairs containing 512 dependent steps. The primary observable is `CLOCK64_BRACKET_SIM_CYCLES_PER_DEPENDENT_STEP=(end_issue_cycle-start_issue_cycle)/512`.

The durable program receipt reports 50 samples and two warmup batches, while selector `chase_occurrence_0` captures one selected kernel trace containing two complete brackets per warp. Results describe the captured bracket population, not a 50-sample simulator distribution and not an absolute Native/simulator cycle fit.
