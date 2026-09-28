# AutoAWQ split-K address mapping

The exact historical source binds `j_factors1=ceil(N/128)`, flattens `(Mtile,Ntile)` into `blockIdx_y`, and places split `z` outside that product. Therefore `Mtile=blockIdx_y/j_factors1`, `Ntile=blockIdx_y%j_factors1`, and `split_z=blockIdx.x/(ceil(M/16)*j_factors1)`.

The qweight, qzeros, and scales base pointers contain Ntile but not Mtile. For fixed split/Ntile, every Mtile therefore consumes the same static address set (Jaccard 1). Within a split, `Ktile=iteration*split+z`. Split8 is a mod8 interleave, not a contiguous K segment. qweight K tiles are disjoint across splits. Metadata uses `group=floor(Ktile/4)`: z0-3 all touch the even groups and z4-7 all touch the odd groups, producing fourfold metadata-set replication across the eight splits.

For linear block IDs, split is outermost and Ntile changes fastest inside each Mtile. Reusing the same Ntile in the next Mtile has distance 384 and 383 intervening CTAs/Ntiles. This is only a static linear-ID proxy; CUDA may schedule CTAs differently, and no cache hit/replacement result follows from it.
