# Platform requalification decision

Decision: `RTX4080_ADA_PLATFORM_QUALIFIED`.

- median absolute error: `12.2112%`
- mean absolute error: `22.8397%`
- worst absolute error: `44.1950%`
- essential point beyond 2x: `NO`
- tuning performed: `NO`

H_CACHE remains a single bounded outlier. H_STREAM and H_COMPUTE independently pass with matched trace-scale Native timing. The unchanged config is frozen as `RTX4080_ADA_ACCELSIM_BASE_V1`.
