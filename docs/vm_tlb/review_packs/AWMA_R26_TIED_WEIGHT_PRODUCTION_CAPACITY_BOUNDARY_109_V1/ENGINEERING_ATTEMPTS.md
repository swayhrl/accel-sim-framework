# Engineering attempts

The first common-start wrapper incorrectly required bitwise equality with the R25 receipt. An exact R25 runner replay also produced different W/m/v hashes while reproducing both RNG hashes, and no parent snapshot payload exists. The final implementation records the mismatch and freezes one accepted-semantics B1 B0 derivation. No optimizer, reducer, tolerance, input, model, or capacity classifier changed. All B1 gates were run after this fix and passed before implementation freeze.
