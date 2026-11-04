# Historical retirement closure — Node109

Oct28 prior actions are historical facts, not actions taken on Nov04. The prior non-ImageLab retirement receipt reports `status=COMPLETE`, 18 files removed for OLMoE and Llama, source and true164 full SHA pass, restore pass, unique allocated bytes released `16323448832`, and observed `df` free delta `16322977792` bytes. Nov04 source OLMoE revision and Llama revision are absent; true164 OLMoE and Llama archive directories and their small receipts are present. This audit did not rehash full target weights.

The prior ImageLab LTX receipt reports two authorized files unlinked, allocated bytes `9619058688`, observed free delta `9619062784`; Nov04 both source paths remain absent, while their Oct28 archive files are present in the full snapshot. Those released bytes are already included in current root free space and must **not** be counted as new cleanup potential.

Three other Oct28 ImageLab H3 source weights are also absent on Nov04 (int8 diffusion, NVFP4 encoder, int8 VAE), while the corresponding Oct28 true164 snapshot files remain. The supplied OLMoE/Llama and LTX retirement receipts do not explain these three absences. Record as `SOURCE_CHANGED`, with zero current releasable bytes, and seek the separate owner/change receipt before interpreting their retirement history. Four Oct31 WAN22 I2V files absent today were in a later six-file true164 snapshot; this audit did not receive a source-retirement receipt for them either.

The Nov04 audit made no source changes. Repeating deletion for any absent path would be an error. The exact retired source/target mapping and current zero-byte status appear in `SOURCE_TO_TRUE164_ARCHIVE_MATRIX.csv`.
