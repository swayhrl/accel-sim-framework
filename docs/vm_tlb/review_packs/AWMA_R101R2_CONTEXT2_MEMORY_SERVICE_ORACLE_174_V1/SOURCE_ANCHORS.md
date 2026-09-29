# Source and artifact anchors

Evidence labels follow repository `AGENTS.md`.

## Authorities

- coordination handoff: `8542a4d37372d586591ff9911929e523645e88f5`;
- accepted R101 architecture parent:
  `8da4057b3c168543603401b1b42a99b556d98042`;
- producer: `bb902283b7ce9e1902b460383fbd3e0bedbd884d`;
- accepted platform:
  `AWMA_RTX4080_SIM_BASELINE_V1 @
  8d1f14a32f5538660d74da86ccb03a2c504c5735`;
- Round-14 note: `fb4d4292b9987a693c988b9ef2115de0c92c8a1f`.

## Frozen simulator artifacts

- unified binary:
  `c43ff6c13c70300c52d2a5cee0611f900ef03d7332292a4227a80f0977b23705`;
- dynamically loaded Core library:
  `7ec99fdb6539d1daa7b499b19f5921d3e742255dcc59f971c2a39e5c1f64c05e`;
- O2 Core patch:
  `cfa2dcc9b9089f884bd1cb1f2d58526fb04f803ed81a8c1d7f6a265653edbc63`;
- framework terminal-drain source:
  `c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323`;
- platform config:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`;
- trace config:
  `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`.

## Derived CONTEXT2 input

- derivation tool:
  `42f24e127058039b50d765e59024b835a30646defc033e70182fb138ef6959ba`;
- derivation receipt:
  `b560ee7a6947854f9123ce739af5befe788d2e17caa74292ca0a0b9a4597882d`;
- kernels table:
  `a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65`;
- runtime sidecar:
  `67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5`;
- kernelslist:
  `73f3d8c9546c06fb81aee209868c9e15e61b0bcfb900b5435c83d520e782748a`;
- ordered six-member trace binding:
  `4fee01b73c9076378aeb583ea65254c5d3882c71ab2d0f2aeac857bc25edf2ce`.

## Frozen formal tools

- Core-patch builder:
  `cf713e9233261a1e43eb8233d955450a45ea14367700016362df81bf60142148`;
- isolated runtime builder:
  `2df9ef5abea80eee482cf9c51d5f9e114ab7f8111ccae33732696508cb1765cd`;
- regression runner:
  `07ce3c6d8df8485f5a99cc13902058ad6bdc48dcb6d8b7ae7d4d72c88cacd5ca`;
- off-equivalence runner:
  `a82f0507b0296d0bf23cc84c50e80d617fac74754dd6671e960cff34ec5259d4`;
- formal runner:
  `bfcc4bf0e067dff0a97987ac4b8f7b3ac2637e740d7403a62b007dcc1b8363db`;
- single-arm summarizer:
  `f3b0beb411f26329c3023f9af80a5a334b1847ba57986bd7936d2542e626a694`;
- cross-arm finalizer:
  `78dec875d6481ea75333955a55e19efc3c4c62f179c03e96707b84e28b7376bf`.

Formal B0/O2 command, log and summary hashes are appended only after atomic
publication. No trace bytes are copied or modified.


## Formal run and recovery receipts

Formal-at-run tools:

- runner:
  `1b55fd7e325dd63496bdb45285bc3f10a63740e2a502873a6c9217aef3305158`;
- original summarizer:
  `cb012f08d7f8ea1c099bb3c4b86e4a13e184ad28f5e2ce20df1c2a4aaa6f8949`.

B0 command / immutable log / recovered summary / recovery receipt:

- `e9029352eae226fd4db91e7cc74f0f6446b347aa9037cef29404075452df9f35`;
- `f1bf0eb5e2e8e22f32f88c6f7a153d4f92cade14031ea8fcf7d50bca24cf4e3c`;
- `2c7e2cac39d0cbc1d0b1a1bf6eb4a0ec43c571b4595b4c282e93e9d4e966f24b`;
- `da99fe29b0e6c8b24f5e5c7c7fd1a0ac63dc43461f560264ade4214f8bbed118`.

O2 command / immutable log / recovered summary / recovery receipt:

- `f96fa5153e783292a554d43d7374904b53b01cd5d3e63dd64cf8fa0cbb0e6cba`;
- `b053eadf7fde2c7dd8eb6c0d4e0306ba4d59810f60aa57ff3b77801ba5ce692e`;
- `d8aba6635e29b920266964fc6e8b2c5cda70cc5ccc1b80985de32420cdc8857f`;
- `918d6cd83162fe70fc9bddc2c5e556ad5b9a115e042a5332fa478521c43bd53a`.

The current runner/summarizer/finalizer hashes above include the postprocessing
fix. Recovery receipts prove raw command/log/stderr/rc bytes are unchanged.


## Raw closure

- raw-index builder:
  `a89342774a64fa68f5a1b2def14c209d6e5bb27b0e4665b6582d63dfaef89e96`;
- `RAW_DATA_INDEX.tsv` (112 evidence rows):
  `18c82eb41c25e1fb1659e5f3c2145dcdb5213c4fb2126b03539ace5b781489ae`;
- node164 `NODE164_EVIDENCE_SHA256SUMS` (61 entries):
  `7c6133c74ed919e886658df0a74da0d26c8a8a4fd3a29b9dcbe10de9a49e24a6`.
