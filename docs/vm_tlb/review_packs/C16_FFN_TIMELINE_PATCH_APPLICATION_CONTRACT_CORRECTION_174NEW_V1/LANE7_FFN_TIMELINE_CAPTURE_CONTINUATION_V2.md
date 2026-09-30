# Lane7 FFN timeline capture continuation V2

This addendum supersedes only the patch-application instruction in the original continuation. It does not alter the authorized scientific contract or capture counts.

1. Read `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json` and require SHA256 `cc081ee281b672bd8ff76cb8ae3e226194c0eec44f6f8916ed4fbbfb8facd2f9`.
2. Discard the prior patched runner and check out `util/vm_tlb/c16/e1_operator_family_natural.py` exactly from `eae1cc4d831ae8459da558cf1358bb8daf8d76e6`. Require SHA256 `902bd8993483290850072afc37245aa7ba80afd821952c7a91fabec0b8e18ea5` before applying anything.
3. Materialize patch `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch` from authorization commit `08f38d7163da95e895aaba10d72231a6d350dfe2` and require SHA256 `06cc0656125e0d5900330f6576b071637de1d09a7e1c9f501929d5577b1361be`. Do not modify its bytes.
4. **Do not use `git apply`.** From the repository root, apply only with GNU patch using:

   ```sh
   patch -s util/vm_tlb/c16/e1_operator_family_natural.py < docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch
   ```

5. Immediately compute the runner SHA256. Continue only if it is exactly `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`; every other SHA is an immediate STOP.
6. Then follow the unchanged authorization: one OFF/ON neutrality pair and, only after it passes, one lightweight NSYS `cuda,nvtx` formal capture under the same GPU lock/budget/publication rules.

The known rejected `git apply` result is `4e4a6061ded405b79cd41bafdd2c74ec7ac92e0e54a1ae9c208ee49b335107bf`. It is malformed and must never be repaired in place; restart from the accepted base instead.
