# M0a reason semantics

`any_blocked_cycles` is the exact once-per-observed-frontend-cycle blocked total.

Per-reason fields are production-visible, stage-primary accounting from the actual preview path. They are not an exhaustive independent all-resource multi-cause bitset: early preview returns and the prioritized MSHR `full_reason` can prevent later reasons from being seen. Do not sum the reason fields, and an absent later reason does not prove that resource was available in a cycle stopped earlier.
