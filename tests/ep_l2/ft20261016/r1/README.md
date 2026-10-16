# R1 diagnostic vectors

Core source be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de integrates the reviewed Lane 4 patch on exact R0 126394be. Append off.config to the unchanged R0 B16 ordered configuration for a same-R1-binary B16 baseline. Each other file differs only in the three ideal flags; these bytes match Lane 4 publication 96fbcb612773900fd75268ffe4e00ed9f13d3d42.

R1 is a separate candidate requiring Lane 5 independent qualification. R0 remains the primary B16/U_WB16 experiment release and is not replaced or blocked. No R0 numerator may be used as a strictly matched R1 ideal baseline. I_WB retains actual copy/read, WAD, queues and DRAM; I_META relaxes allocation capacity only; I_READ_HIT is a standalone optimistic demand-read reference. TVD/RO stay OFF.
