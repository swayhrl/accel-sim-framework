# Scientific boundary

GROUP_M16 is a classic grouped/swizzled software scheduling baseline, not a new mechanism. This experiment tests whether placing the 16 M tiles sharing each N tile consecutively in logical block-ID order restores L2 reuse for this exact AutoAWQ kernel and proxy shape.

Logical block-ID order is not proof of physical GPU issue order. Results cannot be generalized to all W4 kernels, all GEMMs, or a complete GPT-3 deployment. If the strong baseline removes most split8 benefit, the project must credit software ordering and downgrade new split-mechanism space; only a clear residual after the baseline motivates new mechanism design.
