# Final decision

`R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT`

S2 qualifies numerically, never materializes a formal full VxH gradient, and
reduces measured target peak allocated memory by 773.06 MiB versus B0 and
795.58 MiB versus S1. Its target-region timing is stable faster than S1 in all
three groups and stable faster than B0 in two groups; one B0 comparison is a
stable 0.60% regression. Therefore timing is mixed rather than stably worse and
does not meet the two-group regression requirement for
`R24_CAPACITY_TIME_TRADEOFF`.

S1 is not sufficient: although it shortens full-gradient lifetime by 18.86%, it
retains full materialization, raises measured peak memory, and is stably slower
than both B0 and S2 in all three groups.

This is a bounded software/dataflow result only. No hardware promotion,
full-training claim, second shape/model, or automatic follow-on is authorized.
