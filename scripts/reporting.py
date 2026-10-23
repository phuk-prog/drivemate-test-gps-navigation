"""Strict result validation. Counts alone never establish that the intended checks ran."""
from collections import Counter

def validate(cases, expected_ids, process_exit, parse_errors=()):
    actual = [c['id'] for c in cases]
    expected = set(expected_ids)
    errors = list(parse_errors)
    if not expected or len(expected_ids) != len(expected): errors.append('invalid expected test manifest')
    if any(n > 1 for n in Counter(actual).values()): errors.append('duplicate test identity')
    if set(actual) != expected: errors.append('missing or unexpected test identity')
    if any(c['passed'] is not True for c in cases): errors.append('failed, errored or skipped test')
    if process_exit != 0: errors.append('Gradle process failed')
    return errors
