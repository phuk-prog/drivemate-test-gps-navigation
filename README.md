# DriveMate GPS and navigation acceptance

Public synthetic test contracts and sanitized results for checklist Category 1. Application source stays in the private app repository. No real journeys, coordinates, logs, keys or APKs are published here.

Run in an authorized private workspace with the Android SDK, JDK 17 and Gradle dependencies available:

```
python3 scripts/run.py --app /private/checkout --phase baseline --production-base APP_SHA
```

Repeat with `--phase after` using the identical contracts. `final` is a separate run; additional independent edge-case contracts are recorded separately. Gradle logs remain local and ignored. The runner executes the real app's Kotlin classes, not a replacement navigation implementation.

The baseline records absent continuous-uncertainty support explicitly; those cases cannot measure an absent implementation. Passing domain tests does not certify Android permissions, sensor registration, map gestures or road readiness. Device acceptance remains required.

## Device acceptance still required

Use a parked phone or controlled simulator for these checks; no distracting interaction while driving:

- Begin with precise location, then revoke it or disable location; lane diagrams and spoken lane claims must stop without waiting for the visual warning.
- Hold uncertain positioning for less than three seconds, recover, and repeat; the label must only appear after continuous uncertainty, then clear on recovery.
- Pan during GPS loss and wait more than ten seconds; keep that view, retain the last position, and verify the explicit recenter control.
- Background and reopen the app while GPS is uncertain; it must not force a new camera position. End navigation while backgrounded and verify providers, sensors and the uncertainty observer stop.
- Test phones without a gyroscope/gravity sensor and denied sensor registration; navigation must continue using measured GPS without a crash.
- Check the actual map, instruction card and Android Auto for stale lane claims. JVM tests do not measure real GPS accuracy or Android rendering.

`python3 scripts/compare.py` verifies the identical 19-case before/after contract and requires 24 additional final edge cases. The three baseline cases for the absent uncertainty policy are reported as missing support, not physical timing measurements.

## Category 1 comparison — 23 October 2026

| Check | Result |
|---|---|
| Unchanged app baseline | 10/19 acceptance checks passed |
| Candidate, identical acceptance inputs | 19/19 passed |
| Separate final verification | 43/43 GPS checks passed, including 24 additional edge cases |
| Existing map regressions | 8/8 passed |
| Runner infrastructure checks | 2/2 self-tests passed; not counted as app behaviour tests |
| Whole-app verification | 51/51 tests; lint 0 errors and 108 warnings; debug assembly passed |
| Device acceptance | Outstanding; checklist items remain unmarked |

See `results/comparison.json` for the calculated comparison, `results/evidence.json` for exact commits and source identity, and `results/coverage.json` for each checklist requirement and remaining gaps. The candidate is in [private app PR #4](https://github.com/phuk-prog/drivemate-app/pull/4); production main is unchanged. CI executes on that private PR. No app source or APK is published here.

Private [GitHub verification run](https://github.com/phuk-prog/drivemate-app/actions/runs/39966405982) passed for candidate `d4089ce908d4948f42f1067f2ef4f56ba1c30385`: 51 app tests, two runner self-tests, source scan, lint and debug assembly. Physical-device checks remain outstanding.
