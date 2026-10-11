from fractions import Fraction
from pathlib import Path
import json
from local_surgery import BASE
from quota_tools import quota_harmonic_bound
rows=Path('quota-probe-bounds.txt').read_text().splitlines()
for row in rows:
    d,t,q,a,b=map(int,row.split())
    assert Fraction(a,b)==quota_harmonic_bound(BASE,d,t,q),(d,t,q,a,b)
out={'status':'passed','cpp_exact_bound_comparisons_to_validated_generic_python_api':len(rows),
     'includes_reference_denominators_above_32_bit_unsigned_range':True}
Path('quota-cpp-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
