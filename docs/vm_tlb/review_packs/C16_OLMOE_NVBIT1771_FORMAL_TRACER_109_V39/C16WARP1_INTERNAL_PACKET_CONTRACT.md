# C16WARP1 internal Channel packet

`c16warp1_packet_t` is exactly `uint64_t sequence` followed by one historical
280-byte `c16warp1_wrec_t`.  It is not the on-disk format.

The producer gives an active warp one ticket after predicate and CTA filtering.
The first active lane gathers all 32 lane addresses and creates one packet.  A
second device counter gates `ChannelDev::push` by ticket, preventing concurrent
warps from reordering a valid monotonic sequence in Channel arrival order.

The receiver accepts a packet only when its static index matches and its sequence
equals the next expected value.  A malformed, gap, or duplicate packet is not
silently accepted and is persisted in accounting.  At official Channel closure,
the receiver's WRec vector alone is serialized as C16WARP1.
