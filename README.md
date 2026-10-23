# DriveMate GPS and navigation acceptance

Public synthetic test contracts and sanitized results for checklist Category 1. Application source stays in the private app repository. No real journeys, coordinates, logs, keys or APKs are published here.

Run in an authorized private workspace with the Android SDK, JDK 17 and Gradle dependencies available:

```
python3 scripts/run.py --app /private/checkout --phase baseline --production-base APP_SHA
```

Repeat with `--phase after` using the identical contracts. `final` is a separate run; additional independent edge-case contracts are recorded separately. Gradle logs remain local and ignored. The runner executes the real app's Kotlin classes, not a replacement navigation implementation.

The baseline records absent continuous-uncertainty support explicitly; those cases cannot measure an absent implementation. Passing domain tests does not certify Android permissions, sensor registration, map gestures or road readiness. Device acceptance remains required.
