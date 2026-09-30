# Engineering notes

Two CPU authority constants were corrected before GPU execution: a copied
snapshot SHA had one extra character, and the parent pack-manifest constant used
a chat-transcription value rather than the committed file hash. Direct file
hashes and the scientific parent commit were authoritative.

The source patch applied cleanly to the pinned archive and reproduced the exact
patched files. Directed and formal runs had no repair attempts, deadlocks,
timeouts, or profiler retries.
