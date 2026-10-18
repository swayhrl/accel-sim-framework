# Source-bound resume, not repetition of accepted tests

Optional --resume reuses only complete per-mode receipts with returncode0,
exact fixture/source hashes and decoded accepted binary SHA. Full dimensions,
GEN width and full-top mode remain those of the original invocation. Partial
compiled binaries are archived with their own digest and are not PASS. Any
source/fixture change rejects reuse; it never silently validates a new source
using an old executable. Lane3 now saves each completed real RTL byte mode.

These engineering driver changes have only been parsed at the resource hold;
they are not runtime/test evidence. The canonical five hardware files remain
unchanged since e8d67d13 (final static fill specialization). All older R3B0
owner/concurrency PASS rows stay bound to d74b38fc. The new static-specialized
source must obtain its own actual production runs after legal admission.
