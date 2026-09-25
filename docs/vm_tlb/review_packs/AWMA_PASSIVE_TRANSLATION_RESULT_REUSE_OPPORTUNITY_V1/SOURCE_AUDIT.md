# Source audit

Parent source: A2 attribution `b8a4064cb1bbe832758acf9dceb1461844c1fe4e`.
Observability design authority: `b85d388abe98e5da70b749b52075c33fad7cede4`.

The delta adds `passive_translation_memo.h/.cc` and four read-only hooks in
`shader.cc`: decision observation, natural applied-completion observation,
instruction retirement, and final printing. No translation-controller,
READY, lookup, MSHR/PTW, scheduler, accessq mutation, cache, memory, or
arbitration source is changed.

The feature is opt-in through `GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER=1`; OFF
returns before state allocation/traversal and emits no memo records. The same
binary reproduces every accepted baseline signature with observer OFF and ON.

- binary SHA256: `2cf75c70846a042d4154ef0ce5b24f755725e93e1cbe97442318f0fdd8c7ee04`
- observer patch SHA256: `bd7b1862c0801aedb1302689b5a0a0f7bfbd1cefc7a25929cf627e2b550f0b5e`
- patch dry-run: PASS
