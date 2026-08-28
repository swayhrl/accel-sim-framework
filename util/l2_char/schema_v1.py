"""Stable schema helpers for L2CHARV1 parser output."""

SCHEMA_VERSION = "L2CHARV1"
REQUIRED_SLICE_FIELDS = ("slice", "cycles", "mshr_avg", "missq_avg",
                         "draml2q_avg", "l2dramq_avg")
REQUIRED_WINDOW_FIELDS = ("slice", "window", "start_l2_cycle",
                          "end_l2_cycle", "samples")


def as_number(value):
    if value is None:
        return "NA"
    if value.lower() in ("nan", "na"):
        return "NA"
    try:
        if any(c in value for c in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value
