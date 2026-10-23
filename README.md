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
