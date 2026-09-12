# C16 A fixed-release integration receipt

Integration artifact checkpoint: `2a06944c359a9873ae72c89015eb5235dda2d2ee`.

This integration accepts only G
`b5039e160331db993e226bc02fcdfa811db29911` and C
`fed28d8113c0d92cf3a576645f5d736769aefb12`, after their respective manifests
and every listed payload matched.  The exact identities and manifests are in
`CONSUMED_C16_RELEASES.tsv` and `MANIFEST_VALIDATION.md`.

H `65b5357400db3b4c77f8a60e575091e22fb081ee` is explicitly rejected because it
does not carry a publish manifest or equivalent payload-hash release.  It is not
an input to the C16 GPU package, common-pattern, cost, behavior-class, or final
dynamic conclusion.  Consequently the overall status remains
`C16_LOCAL_PREP_AND_INTEGRATION_PARTIAL_READY_FOR_FINAL_REVIEW`.
