# Wave-1 Roster Reconciliation Review Pack

- Framework branch: `hrl/l2-resource-char-exp-v1`
- Framework source commit: `286e9fc09cd8898a6e8137669194ab3ac1182677`
- Scope: exact 52-workload roster reconciliation, selected-asset identity,
  physical asset inventory correction, and the application-level multi-kernel
  output-semantics pilot.
- Excluded by design: broad characterization and 159-root bulk body hashing.

## Included files and SHA256

```text
80ef025839a86c36ec532a2a19581953b6e835958aca74eb9abc02bc1191c8b1  docs/l2_char_v1/ROUND1_PREFLIGHT_REPORT.md
02bc7bddbc72eb35812564f6ac84117779773cfca318ef70b087108b6be1b48b  docs/l2_char_v1/ROUND1_PHYSICAL_TRACE_INVENTORY.tsv
335348e84edce46f9bf5f8a54e2edd4d4302f09f8e3f75382e3e4629aefbac98  docs/l2_char_v1/ROUND1_WAVE1_COST_ROSTER.tsv
1946214b24f7b139f78013aa30a446373e776a4849d121284f4e6f15d00cdda1  docs/l2_char_v1/ROUND1_WAVE1_ROSTER_SUMMARY.md
c7724e0db63dc5a99a5b9744cb83b4f9390ae5bd81a100ba9767d56c4168513f  docs/l2_char_v1/ROUND1_WAVE1_TRACE_MANIFEST.json
56dabe7678a6662be09472db8485900d4bdd2f5319a6ff88b7ee84d3a7adc9cb  docs/l2_char_v1/round1_pilots/fastWalshTransform_11_19/manifest.json
d286ba73546f754a308363c5d01814a5bb3996d6629e4eab376d1ec8bcc68c0b  docs/l2_char_v1/round1_pilots/fastWalshTransform_11_19/summary.csv
a23a853679200379094c55f45fd9b821752461d20d41ee36b5d589cbcbdaf1bd  docs/l2_char_v1/round1_pilots/fastWalshTransform_11_19/slice.csv
4e071853c410fcd616d8fbf5664f4e49de0db141963001c860cde5b426e54fa9  docs/l2_char_v1/round1_pilots/fastWalshTransform_11_19/window.csv
090ca02d44d465a085b7d877c831f86c40ebb0b0536cd5eccfca70b98045bdc6  util/l2_char/build_round1_trace_inventory.py
ec2d1176ff5ce2b028aa1b1a52c49805190740e13207eb7b9f75c82b706fc9c8  util/l2_char/build_round1_wave1_roster.py
743b9238e92afee975e5d82ca2954ec84a39011753eb375dfef53b2249268a0e  util/l2_char/hash_round1_wave1_traces.py
```

The associated `.tar.gz` preserves these repository-relative paths and this
contents file. Verify the archive after extraction with `sha256sum -c` using
the block above (after removing the Markdown fence).
