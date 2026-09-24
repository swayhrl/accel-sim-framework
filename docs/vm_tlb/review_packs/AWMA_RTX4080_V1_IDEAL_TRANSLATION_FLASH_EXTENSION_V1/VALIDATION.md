# Validation

Both ideal runs completed with rc=0 using the frozen V3 binary.

- accepted payload and runner-index SHA256 identities matched before launch;
- instructions, CTA and unique UID coverage matched accepted authorities;
- untranslated=0, unobserved=0 and duplicate attempts=0;
- terminal quiescent invariant = 1;
- L1/L2 modeled lookup launches = 0;
- translation lookup/MSHR/PWQ/walker/PTW/PWC/PTE activity = 0;
- functional mapping digests were emitted for both targets.

No other target or mechanism was executed.
