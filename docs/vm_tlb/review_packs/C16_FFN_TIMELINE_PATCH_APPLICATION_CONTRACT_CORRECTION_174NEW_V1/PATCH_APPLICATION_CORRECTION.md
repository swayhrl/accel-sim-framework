# FFN timeline patch application contract correction

This is an engineering-only correction to authorization `08f38d7163da95e895aaba10d72231a6d350dfe2`. The authorized scientific contract, model/input/runtime/scenario identity, instrumentation patch bytes, measurement protocol, GPU budget, and OFF/ON plus formal-run counts are unchanged.

CPU reproduction starts from `eae1cc4d831ae8459da558cf1358bb8daf8d76e6:util/vm_tlb/c16/e1_operator_family_natural.py` (SHA256 `902bd8993483290850072afc37245aa7ba80afd821952c7a91fabec0b8e18ea5`) and the authorized patch (SHA256 `06cc0656125e0d5900330f6576b071637de1d09a7e1c9f501929d5577b1361be`). From the repository root, GNU `GNU patch 2.7.6` with the exact command below reconstructs the authorized runner SHA256 `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`:

```sh
patch -s util/vm_tlb/c16/e1_operator_family_natural.py < docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch
```

Plain `git apply` returns success but yields SHA256 `4e4a6061ded405b79cd41bafdd2c74ec7ac92e0e54a1ae9c208ee49b335107bf`. Its zero-context insertion hunks are relocated to the file tail; the instrumentation is outside `main` and the result fails Python syntax validation. Therefore `git apply` is explicitly prohibited and cannot satisfy authorization.

Lane7 must discard any previously patched working copy, restore the accepted base bytes, use the exact GNU patch command, hash immediately, and continue only on exact `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`. Any other result is an immediate STOP.
