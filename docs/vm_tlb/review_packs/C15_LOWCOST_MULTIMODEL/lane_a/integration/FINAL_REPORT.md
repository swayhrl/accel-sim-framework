# C15 low-cost foundation — partial ready for review

Status: `C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_REVIEW`.

Lane A has completed the bounded static foundation: ten immutable-revision
deployment configurations across nine model lineages, including a raw/AWQ pair;
three complete Safetensors-header storage catalogs; seven standard-KV static
formula configurations; and explicit exclusions for MLA/compressed or
insufficiently specified configurations. Seven storage configurations remain
config-only. No full weight was downloaded.

Lane A consumed B only from commit `721e30f377dab36d826dc7ea9d47e11c5d85aa5c`
and C only from commit `a51d6c91b1e7d7df27a4af80823a29ff30bb9806`; their
manifest and selected-payload hashes were checked before synthesis. B provides a
capability-limited, trace-header-only checkpoint with zero new native GPU run,
native timing, SASS, or capture trace. C provides historical C12/C13 validation,
but its sampler is `SAMPLER_NOT_QUALIFIED` and it reports no new simulator, GPU,
or trace measurement.

This publication therefore contains no dynamic cross-model conclusion and grants
no upgrade authorization. No model speed, cycle count, miss rate, translation
behavior, cache/TLB conclusion, GPU address claim, or runtime ranking is
asserted. `UPGRADE_DECISIONS.tsv` makes the missing preconditions explicit;
future work requires fresh authorization after a committed native capture and a
qualified sampler are available.

Every output in this directory is an A-owned integration record. It consumes only
the producer commits and manifest-bound files named in `CONSUMED_INPUTS.tsv`; it
does not merge, copy, or modify B/C artifacts.
