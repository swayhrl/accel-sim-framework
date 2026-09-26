# Verification checklist

- [x] coordination HEAD exact
- [x] directed semantic model PASS (10 cases)
- [x] final-binary OFF signature exact on T2
- [x] seven reference full-kernel runs PASS
- [x] seven PREL1 source-observer runs PASS and exact frozen cycles
- [x] instructions / CTA / logical coverage closed
- [x] untranslated=0 / unobserved=0 / duplicate=0
- [x] terminal controller and reference quiescence
- [x] functional mapping digest has zero conflicts and matches per target
- [x] exact within-run intersection/difference/UNKNOWN reported
- [x] true L1/L2 launch, MSHR/PTW/PTE and downstream traffic fields retained
- [x] replay budget <= 18
- [x] no 109, recapture, platform change, or extra mechanism
