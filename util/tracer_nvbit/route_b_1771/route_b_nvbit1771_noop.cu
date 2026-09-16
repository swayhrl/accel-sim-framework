#include "nvbit_tool.h"

/* Isolated Q05 compatibility probe: no context callback, no channel, no
 * payload and no lifecycle replacement.  It distinguishes NVBit-core runtime
 * compatibility from Route-B callback/data-plane behaviour. */
void nvbit_at_init() {}
