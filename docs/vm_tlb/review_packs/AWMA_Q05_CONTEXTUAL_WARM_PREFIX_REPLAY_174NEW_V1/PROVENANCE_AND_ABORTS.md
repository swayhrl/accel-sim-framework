# Non-scientific pre-runtime attempts

The first P1 attempt lacked the preserved runtime `libcudart.so`; the second mistakenly supplied raw `.trace.xz`, while the accepted simulator parser consumes `.traceg.xz`. Both exits occurred before simulated cycle progress, are retained in node164 raw provenance, and were corrected by binding the preserved local libcudart and using the independently validated traceg members. Formal rows are only `*_traceg`, each with exit status 0.
