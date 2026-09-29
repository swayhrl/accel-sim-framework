# Strict conversion identity

Identity = `(qweight K32×N128 logical range, qzeros G128/N128 range, FP16 scales G128/N128 range, AutoAWQ packed INT4 affine format, zero/scale decode semantics, FP16 target operand dtype, m16n128k32 transposed B_shared/ldmatrix operand layout, CUDA half2 rounding/packing semantics)`。仅相同qweight地址不足以判同。不同K32即使共享metadata也产生不同conversion result。
