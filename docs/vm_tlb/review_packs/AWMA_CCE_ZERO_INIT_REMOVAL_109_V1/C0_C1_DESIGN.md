# C0/C1 design

C0 is the pinned CCE exact/no-filter path with FP32 classifier-gradient
accumulation initialized by torch.zeros_like.

C1 changes only dC initialization:

1. It allocates the same full FP32 dC with torch.empty_like.
2. It reuses the existing 128x64-tile dCLocks array.
3. State 0 is uninitialized/free, state 1 is initialized/free, and state 2 is
   held by either the first initializer or a later updater.
4. The first writer atomically claims state 0, stores its full valid tile
   contribution without reading dC, and publishes state 1.
5. Later writers claim state 1, load/add/store, and return to state 1.
6. If the compacted valid-token count is zero, C1 falls back to the original
   zero allocation and disables first-store mode.

The existing 16,618-entry int32 lock array is 66,472 bytes and is reset inside
the measured boundary. No additional state bytes, full-size shadow buffer,
lazy full-size zero pass, future ordering, precision change, chunking change,
or heuristic retuning is used.

Both arms use CCE_AUTOTUNE=0 and identical BLOCK_B=128, BLOCK_V=128,
BLOCK_D=32, MM_BACK_BLOCK_D=64, num_warps=4 and num_stages=4.
