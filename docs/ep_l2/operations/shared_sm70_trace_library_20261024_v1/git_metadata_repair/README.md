# Canonical integration metadata repair

The unpublished primary sparse integration had duplicate/unsorted Git tree
objects. The source lane original72a5037 was independently strict-fsck clean.
A separate complete-index integration rebuilt its changes from valid cdbf3ae,
then copied the exact owned IO/audit blobs from unpublished85d98ac.
All2933 unique paths, modes and blob IDs are identical before/after; no working
file, source, trace, consumed scientific spec, or old scientific commit changed.
The original commits, objects, index and bundle remain retained for inspection.
A reachable-only isolated bare clone without alternates passed strict fsck.
The primary worktree now has a full dense index and complete checkout, so later
integration does not rely on sparse directory/cache behavior. The exact lower
level cause beyond the observed invalid primary integration remains unproven.
Future publication requires a reachable-only strict check; all repair refs are
local and the public branch update remains a normal fast-forward.
