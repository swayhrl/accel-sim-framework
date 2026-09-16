# Capture recovery receipt

The first V20 S2 capture attempt used the pre-existing MREF-address callback for all eight frozen direct-GLOBAL static instructions. Its CTA coverage was complete, but the four LDG source shards produced address zero; therefore it failed the same-process `KV_POST_UPDATE_K` source-range gate and was never admitted.

The correction did not change model, input, precision, backend, semantic target, static function, or capture capacity. It rebuilt the NVBit callback with a register-pair source-address path for the known SASS LDG address registers (`R4:R5` for static indices 237, 475, 713 and `R2:R3` for 950), while preserving the normal MREF destination-address path for STG instructions. The repair was first tested on static 237 and then used for fresh S2 and S3 capture roots.

The accepted fresh captures have full CTA coverage and source-load address membership in `KV_POST_UPDATE_K`; the rejected local diagnostic root was not promoted, transferred, cataloged, or ACKed.
