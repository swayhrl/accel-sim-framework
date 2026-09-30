# Final decision

CCE_ZERO_INIT_SOFTWARE_REMOVABLE

C1 passed all seven directed categories across 14 C0/C1 pairs, including
all-ignore fallback and eight repeated contended launches. The accepted real
shape passed loss, grad_hidden and grad_weight at the frozen rtol=atol=1e-2.

C0 median was 8.171520 ms and C1 median was
7.202816 ms. The paired counterfactual recovered
0.968704 ms, or
11.85% of the complete operator and
128.85% of the accepted
0.751779 ms zero-fill anchor.

The full-operator delta is not identified one-for-one with the old fill; first-writer lock scheduling changes are part of the software counterfactual.

The one C1 NSYS capture proves the full zero-fill disappeared without an
equivalent pass while the small state reset, final BF16 cast, CCE backward and
LSE work remain. On this frozen shape the prior residual is primarily a software
accumulation-organization artifact. This does not authorize a second shape,
hardware mechanism, or end-to-end claim.
