# rounding.py
import math

def normal_round_to_whole(x):
    # normal rounding to nearest whole number
    # follow standard: .5 rounds up
    return int(round(x))

def round_down_whole(x):
    # pediatric dosing - always round down to avoid overdose
    return math.floor(x)

def round_to_tenth(x):
    return round(x, 1)

def round_to_hundredth(x):
    return round(x, 2)

def format_leading_zero(x):
    # Ensure leading zero for decimals less than 1 (e.g., 0.5)
    s = str(x)
    if isinstance(x, float):
        if 0 < abs(x) < 1 and not s.startswith("0"):
            return "0" + s
    return s

def apply_rounding(value, rule):
    """
    rule: "normal" | "pediatric" | "tenth" | "hundredth"
    IMPORTANT: caller must ensure rounding is applied ONLY to the final numeric answer.
    """
    if value is None:
        return None
    if rule == "pediatric":
        return round_down_whole(value)
    elif rule == "tenth":
        return round_to_tenth(value)
    elif rule == "hundredth":
        return round_to_hundredth(value)
    else:
        return normal_round_to_whole(value)
