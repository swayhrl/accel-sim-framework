# Mechanism freeze

- candidate: `nonblocking_opportunistic_share`
- fanout threshold: none
- delivery: accessq head only, at most one shared member per cycle
- fallback: immediate frozen V1 path; permanent late-result exclusion
- owner/fallback cancellation: none
- binary SHA256: `fa4346fcb4b4bddcf493606b7ce3e87ccd3e6241c26258f62c2c0cb79d4cda47`
- Core patch SHA256: `81b2b6c0d2f0e30d50b46ca66ab010910c289f1afbb4da7e3f17bc93e4ccdac6`
- source frozen before A1 and the five development performance runs
- no source or parameter change after directed-test PASS
