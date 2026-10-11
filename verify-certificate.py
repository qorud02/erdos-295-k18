"""Exact certificate check; Python >=3.9 standard library only."""
from fractions import Fraction
from math import lcm
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
D = [
    18,19,20,21,22,23,24,25,26,27,28,29,30,31,
    32,33,34,35,36,38,39,40,43,44,45,46,
    48,50,52,54,63,275,14143068,10457416992,
]
OLD = [
    18,19,20,21,22,23,24,25,26,27,28,29,30,31,
    32,33,34,35,36,38,39,40,42,43,44,45,
    48,50,52,54,63,640,337280,1735650,68479214496,
]
LEFT = [42,640,337280,1735650,68479214496]
RIGHT = [46,275,14143068,10457416992]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def reciprocal_sum(ds):
    return sum((Fraction(1,d) for d in ds), Fraction())

cert = json.loads((ROOT / "certificate-34-independent.json").read_text(encoding="utf-8"))
require(D == cert["denominators"], "JSON certificate differs from displayed witness")
require(len(D) == len(set(D)) == 34, "Incorrect length or repeated denominator")
require(D == sorted(D) and min(D) >= 18, "Order or minimum violated")
require(reciprocal_sum(D) == 1, "Exact rational sum differs from one")
common = lcm(*D)
weighted = sum(common // d for d in D)
require(common == 6209352774424800, "Unexpected LCM")
require(weighted == common, "Integer certificate fails")
require(str(common) == cert["lcm"] == cert["weighted_sum"], "JSON integer fields differ")
require(cert["terms"] == 34 and cert["distinct"] == 34 and cert["minimum"] == 18,
        "JSON dimension fields differ")
require(cert["sum_numerator"] == cert["sum_denominator"] == "1", "JSON rational fields differ")
require(len(OLD) == len(set(OLD)) == 35 and reciprocal_sum(OLD) == 1,
        "Original 35-term witness fails")
require(set(LEFT).issubset(OLD), "Removed denominator absent from source")
retained = set(OLD) - set(LEFT)
require(retained.isdisjoint(RIGHT), "Replacement collides with retained denominator")
require(sorted(retained | set(RIGHT)) == D, "Surgery does not produce final witness")
require(reciprocal_sum(LEFT) == reciprocal_sum(RIGHT), "Surgery equality fails")
surgery_common = lcm(*(LEFT + RIGHT))
left_weights = [surgery_common // d for d in LEFT]
right_weights = [surgery_common // d for d in RIGHT]
require(surgery_common == 636856694812800, "Unexpected surgery LCM")
require(sum(left_weights) == sum(right_weights) == 16160598373892, "Scaled surgery fails")
result = {
    "status": "passed",
    "claim": "k(18) <= 34",
    "terms": len(D), "minimum": min(D), "distinct": len(set(D)),
    "exact_sum": str(reciprocal_sum(D)),
    "lcm": str(common), "scaled_sum": str(weighted),
    "surgery_lcm": str(surgery_common),
    "surgery_left_weights": left_weights,
    "surgery_right_weights": right_weights,
    "surgery_scaled_sum": str(sum(left_weights)),
    "checks": ["Fraction sum", "integer LCM sum", "35-to-34 surgery", "JSON agreement"],
}
print(json.dumps(result, indent=2, ensure_ascii=False))
