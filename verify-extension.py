"""Verify positive certificates and their source comparisons; standard library only.

Run: python verify-extension.py
All stored denominators are decimal strings, preserving arbitrary-size integers
when the JSON is also read by software with a fixed-precision numeric type.
"""
import copy
import json
from fractions import Fraction
from math import lcm
from pathlib import Path


def check_vector(values, minimum, terms):
    ds = [int(d) for d in values]
    if len(ds) != terms or ds != sorted(set(ds)) or min(ds) != minimum:
        raise ValueError('count, strict order, distinctness, or minimum')
    if sum((Fraction(1, d) for d in ds), Fraction()) != 1:
        raise ValueError('rational sum')
    L = lcm(*ds)
    if sum(L // d for d in ds) != L:
        raise ValueError('integer sum')
    return ds, L


def check_record(record):
    ds, L = check_vector(record['denominators'], record['minimum'], record['terms'])
    if str(L) != record['lcm'] or record['scaled_sum'] != str(L):
        raise ValueError('stored integer certificate')
    old, _ = check_vector(record['comparison_denominators'], record['minimum'], record['comparison_upper'])
    removed = sorted(set(old) - set(ds))
    added = sorted(set(ds) - set(old))
    if sum((Fraction(1, d) for d in removed), Fraction()) != sum((Fraction(1, d) for d in added), Fraction()):
        raise ValueError('replacement identity')
    result = {'minimum': record['minimum'], 'terms': len(ds), 'lcm': str(L),
            'comparison_upper': len(old), 'removed': [str(d) for d in removed],
            'added': [str(d) for d in added], 'status': 'verified'}
    if record['minimum'] in (20, 21):
        residual = 1 - sum((Fraction(1, d) for d in ds[:-2]), Fraction())
        a, b = residual.numerator, residual.denominator
        x, y = ds[-2:]
        q = a * x - b
        D = ds[-3] + 1
        if not (a > 0 and 0 < q < b and q >= a * D - b and q % a == (-b) % a):
            raise ValueError('two-term completion conditions')
        if q * (a * y - b) != b * b:
            raise ValueError('two-term factorization')
        result['two_term_completion'] = {'a': str(a), 'b': str(b), 'q': str(q),
                                         'x': str(x), 'y': str(y)}
    return result


def negative_controls(records):
    tested = 0
    for original in records:
        mutations = []
        r = copy.deepcopy(original); r['denominators'][-1] = str(int(r['denominators'][-1]) + 1); mutations.append(r)
        r = copy.deepcopy(original); r['denominators'][-1] = r['denominators'][-2]; mutations.append(r)
        r = copy.deepcopy(original); r['denominators'].pop(); mutations.append(r)
        r = copy.deepcopy(original); r['minimum'] += 1; mutations.append(r)
        r = copy.deepcopy(original); r['lcm'] = str(int(r['lcm']) + 1); mutations.append(r)
        for mutated in mutations:
            try:
                check_record(mutated)
            except ValueError:
                tested += 1
            else:
                raise AssertionError('invalid certificate was accepted')
    return tested


if __name__ == '__main__':
    pack = json.loads(Path(__file__).with_name('certificates-extension.json').read_text())
    results = [check_record(r) for r in pack['records']]
    controls = negative_controls(pack['records'])
    print(json.dumps({'status': 'passed', 'records': results, 'negative_controls_rejected': controls}, indent=2))
