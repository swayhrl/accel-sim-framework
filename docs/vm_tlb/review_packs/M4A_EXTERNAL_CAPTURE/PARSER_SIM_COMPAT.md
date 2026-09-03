# Parser and simulator compatibility

Using Core `73774727e25fadf89df6f30ef5cf014091115db7`, the retained SM86 RTX
3070 configuration's `gpgpusim.config` plus `trace.config`, each formal full
list started and bound the first ordinary BF16 compute kernel during a bounded
smoke. Since all entries classify COMPUTE, compute-only lists are byte-identical
and inherit the same parser path. This is format compatibility, not a result or
a claim that RTX 3070 config represents RTX 3080 Ti hardware.
