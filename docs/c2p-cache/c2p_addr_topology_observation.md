# C2P+ address/topology observation

This experiment is a read-only feature study for the first decision after a
mandatory peer-probe miss.  It never changes the exhaustive C2P+ candidate
order, target FIFO admission, remote-tag timing, or lower fallback.

For each initial candidate-count bin, it records the same outcome by three
features: a 32-bucket hash of the cache-line tag, requester cluster, and their
cross product.  The outcome is whether a later exact peer exists and whether
it lies within the next four probes.  `lower_ready` and `target_credit` are
sampled at that decision point solely to identify a potentially cheap lower
fallback or a constrained target FIFO.

The campaign uses BFS, LPS, and Btree, each with one exhaustive C2P+ replay.
Its results can justify a later address/topology predictor only if a feature
shows stable, sufficiently populated variation beyond candidate-count bin.
