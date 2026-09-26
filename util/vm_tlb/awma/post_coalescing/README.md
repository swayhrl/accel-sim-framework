# Post-coalescing residual fixtures

These files are directed algorithm contracts, not simulator mechanisms and not
performance evidence.

- `is_last_unresolved_head_group` fixes the online predicate for H1.
- `choose_demand_before_prelaunch` fixes the finite one-port arbitration for
  H2.
- `AccessTimeline` prevents translation wait, READY-result consumption delay,
  and post-translation cache-admission delay from being conflated.

Run with:

```bash
python3 -m unittest -v test_residual_event_model.py
```

No future trace event or baseline completion timestamp is an input to either
decision function.
