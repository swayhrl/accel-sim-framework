# Macro-aware floorplan for twenty 1024x64 ASAP7 SRAM banks.
# Five banks compose each 5120x64 Snapshot replica; four replicas are needed
# for C2P's tag-mask and three Bloom rows.  The core leaves explicit routing
# channels around 30.348 x 77.760 um macro abstracts.
initialize_floorplan -site asap7sc7p5t \
    -die_area {0 0 250 410} -core_area {10 10 240 400}
