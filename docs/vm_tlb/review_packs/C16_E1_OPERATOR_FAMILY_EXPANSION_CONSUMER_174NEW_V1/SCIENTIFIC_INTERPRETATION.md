# Operator-family independent consumer closure

Producer `eae1cc4d831ae8459da558cf1358bb8daf8d76e6` independently closes from raw evidence at `OPERATOR_FAMILY_NOT_SUPPORTED`.

Natural FFN order is raw-derived as gate_proj -> up_proj -> down_proj. All 84 modules, 14 matched conditions, 98 fresh processes, host overhead, 12 multi-pass NCU profiles, and the frozen FULLHINT gate close.

UP28 median direct-up saving is 0.553440 ms while its outside-FFN residual is -0.357706 ms. GUD84 median direct FFN saving is 0.464491 ms and outside-FFN residual is -0.422358 ms. Only 28/84 selected GUD84 modules are material—the up_proj family. No condition has a positive whole-decode effect beyond dispersion.

Negative residual remains an accounting observation with cause unestablished; it is not called cache collateral slowdown. No simulator authorization follows.
