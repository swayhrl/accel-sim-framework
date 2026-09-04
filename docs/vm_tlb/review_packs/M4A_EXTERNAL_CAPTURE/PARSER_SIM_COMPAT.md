# Parser and simulator compatibility

Using parser Core `73774727e25fadf89df6f30ef5cf014091115db7`, the retained SM86
RTX 3070 `gpgpusim.config` plus `trace.config` bounded smoke binds early,
middle, and late semantically classified COMPUTE samples, the one observed
NCCL family, and each corrected compute-only derivative. This is format/startup
compatibility only—not a performance result or a claim that RTX 3070 represents
RTX 3080 Ti hardware. The frozen parser Core is an audit anchor; future Core
must come from accepted final Track-A M1–M3.
