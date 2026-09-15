# Missing after direct inspection

None of the five V1 ODP scopes remains uninspected.  The self-SSH premise was
removed: all checks were local to old174.

No C12--C15 scientific data was found under non-shared `/root`.  `/tmp`
contained the exported C12 pre-fix scan and only limited validator/build
scratch artifacts otherwise.  The narrow pilot-only
`/workspace/vm-m4b-runs-f96b7ea9-5bdd4b55` remains
`PRIVATE_RELEVANCE_UNKNOWN`; it is not a reason to bulk copy unrelated
private roots.  Its omission is explicit, not an SSH or permission blocker.
