# TC80 capacity-matched fairness analysis

All ratios are regenerated from the exact 12 integer-cycle rows in CM3; displayed values are rounded only after the calculation. The classification columns use the declared symmetric 1% presentation window and never replace the numeric ratios.

TC80 is an exact 80-KiB conventional cache: all 80 KiB are ordinary searchable locality capacity. DTC instead couples a 16-KiB logical searchable Tag capacity to an 80-KiB physical data pool. Thus the experiment tests ordinary locality capacity versus decoupled in-flight physical state under the same data-array byte budget. TC80 deliberately has more searchable Tag entries and is a strong conventional-capacity baseline.

This is not a claim of equal total area, timing, power, metadata cost, or a causal attribution solely to Tag/Data decoupling. PIB and MSHR remain the frozen B16 values (8 and 32), so this experiment does not evaluate a large-PIB/large-MSHR conventional cache.

## Geometric means

- `GM_TC80_OVER_B16` = `1.437564501098`
- `GM_IO_OVER_B16` = `1.326143376158`
- `GM_OO_OVER_B16` = `1.592062401603`
- `GM_IO_OVER_TC80` = `0.922493129975`
- `GM_OO_OVER_TC80` = `1.107471978049`
