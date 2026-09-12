# Relative-error units

All `relative_error_fraction` values use `abs(error / reference)` and are unitless fractions. `relative_error_percent` is exactly `100 * relative_error_fraction`. The frozen macro-cycle screening threshold remains `relative_error_fraction <= 0.05` (5%); this closeout changes no PASS/FAIL rule or result.
