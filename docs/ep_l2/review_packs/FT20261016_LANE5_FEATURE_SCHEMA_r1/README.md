# Feature schema migration, r1

47 registry/runner/schema tests PASS. This is tooling evidence, not qualification
of a new TVD/RO production binary. R0 formal simulator/runner processes were not
restarted. Original R0 V1 identities and keys remain exact and unchanged.

Ten frozen R0 formal specs have read-only V2 display projections: legacy ro=false
maps to detach=false, MSHR bypass=false. The projections issue no new run keys,
change no registry records, and grant no new feature qualification. Legacy enabled
ro=true is ambiguous and is rejected. New RO vectors require both explicit bits,
a distinct canonical identity and exact independently qualified feature vector.

Synthetic test certificates exercise validator rejection/acceptance only; they are
never production certificates. The retained production R0 certificate continues
to qualify only the original two V1 feature vectors.
