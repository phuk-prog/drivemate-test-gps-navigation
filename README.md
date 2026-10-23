> **Current execution (2026-10-23): all tests run publicly.** Relevant app components may be published; the combined app and final APK generation stay private. Historical private-CI references below are superseded by [TESTING_POLICY.md](TESTING_POLICY.md).
>
> All 57 existing GPS cases now execute in the [public Batch A workflow](https://github.com/phuk-prog/drivemate-test-map-display/actions/runs/40021527920), plus eight new GPS boundary cases: 65 distinct candidate GPS checks pass. Original comparison 10/19 → 19/19; expanded GPS 11/27 → 27/27; Android adapter 4/6 → 6/6; additional candidate-only verification 32/32. [Exact public evidence and limits](https://github.com/phuk-prog/drivemate-test-map-display/tree/65dd04b70cef4f28195a74b81b46ec8a5a2fc3ae/results/batch-a-public-20261023). Component success is not whole-app acceptance or legal certification. Implementation is staged in private draft PR #8, not merged/released.

# DriveMate GPS and navigation acceptance

## Shared GPS + map + roundabout batch policy

Per the owner's 23 October 2026 instruction, public GPS tests are part of [the grouped public testing plan](https://github.com/phuk-prog/drivemate-test-map-display/blob/main/contracts/grouped-public-tests.json). Combine two to four related categories, e.g., **01 GPS + 02 map route line + 04 lane guidance + 05 legal routing**, when exercising the same real UK roundabout. One pinned source dataset, GPS trace/replay, test runner and necessary test build may serve several categories, but category and checklist pass/fail results remain independent. Source of truth must come from legally usable external UK evidence and dated ground facts, not self-referential app output. Keep source and credentials private; public repo has tests and sanitized evidence only. No release APK unless mandatory replay/robot checks pass.

Latest expanded results and per-preference evidence: [`results/reliability/`](results/reliability/). The original comparison remains preserved in the root results files.

Public synthetic test contracts and sanitized results for checklist Category 1. Application source stays in the private app repository. No real journeys, coordinates, logs, keys or APKs are published here.

Run in an authorized private workspace with the Android SDK, JDK 17 and Gradle dependencies available:

```
python3 scripts/run.py --app /private/checkout --phase baseline --production-base APP_SHA
```

Repeat with `--phase after` using the identical contracts. `final` is a separate run; additional independent edge-case contracts are recorded separately. Gradle logs remain local and ignored. The runner executes the real app's Kotlin classes, not a replacement navigation implementation.

The baseline records absent continuous-uncertainty support explicitly; those cases cannot measure an absent implementation. This workflow uses automated checks: production Kotlin contracts, source checks, lint and APK assembly.

`python3 scripts/compare.py` verifies the identical 19-case before/after contract and requires 24 additional final edge cases. The three baseline cases for the absent uncertainty policy are reported as missing support, not physical timing measurements.

## Shared GPS + map + roundabout test batches (owner policy, 23 October 2026)

Follow the [canonical public grouped test policy](https://github.com/phuk-prog/drivemate-test-map-display/blob/main/contracts/grouped-public-tests.json). DriveMate tests are public contracts, traceable third-party references, shareable fixtures and sanitized per-item results, but real private app source and personal data remain private.

**Run 2–4 related categories in a single coherent test harness/build or internal test APK where appropriate.** Roundabout and junction testing may cover **01 GPS, 02 map/carriageway display, 04 lane advice and 05 routing/turn legality** together on identical dated real UK road geometry, legal-sign evidence and GPS replay. Do not run duplicate APK builds for separate categories when the same run can exercise all the relevant requirements. Accept and report each item separately; keep before/after comparisons and safety/robot gates mandatory. Do not infer 04/05 readiness just because their test group is defined.

The [public map-display test repository](https://github.com/phuk-prog/drivemate-test-map-display) hosts related Category 2 and independently sourced UK-road fixtures. A combined 01/02/04/05 execution is **not** claimed until a linked GitHub run confirms it. For source-integrated tests, private GitHub Actions executes pinned public tests against actual app classes, and public artifacts contain only safe result summaries; no APK, private source, tokens, signing key or TomTom key is publicly published before release gates.

## Initial Category 1 comparison — 23 October 2026

| Check | Result |
|---|---|
| Unchanged app baseline | 10/19 acceptance checks passed |
| Candidate, identical acceptance inputs | 19/19 passed |
| Separate final verification | 43/43 GPS checks passed, including 24 additional edge cases |
| Existing map regressions | 8/8 passed |
| Runner infrastructure checks | 2/2 self-tests passed; not counted as app behaviour tests |
| Whole-app verification | 51/51 tests; lint 0 errors and 108 warnings; debug assembly passed |
| Verification scope | Automated checks only, as requested by the owner |

See `results/comparison.json` for the calculated comparison, `results/evidence.json` for exact commits and source identity, and `results/coverage.json` for each checklist requirement and its automated coverage. The candidate is in [private app PR #4](https://github.com/phuk-prog/drivemate-app/pull/4); production main is unchanged. CI executes on that private PR. No app source or APK is published here.

Private [GitHub verification run](https://github.com/phuk-prog/drivemate-app/actions/runs/39966405982) passed for candidate `d4089ce908d4948f42f1067f2ef4f56ba1c30385`: 51 app tests, two runner self-tests, source scan, lint and debug assembly. The automated verification passed.

## Expanded preference verification

The expanded suite is defined by `contracts/manifest.json`. The runner requires every expected class/method identity exactly once and rejects failures, skipped cases, malformed results and a failed Gradle process. It records fingerprints for both the original 19-case contract and the complete executed suite.

`contracts/preferences.json` maps all four agreed GPS preferences to runtime tests and static source integration guards. `scripts/coverage_check.py` fails if a preference is omitted or points at missing evidence. Static guards are labelled separately from runtime tests and do not claim UI rendering coverage.

Android sensor-adapter tests run automatically using Robolectric 4.14.1 and Mockito 5.14.2 in the private test build; these dependencies are not packaged into the app. Additional combined scenarios include a fixed-seed, 5,000-event uncertainty sequence. The new baseline found one cached-heading reset bug; see `results/reliability/` for the unchanged-suite comparison. The original comparison remains preserved above.

Run the expanded private verification:

```
python3 scripts/run.py --app /private/checkout --phase final --production-base APP_SHA --full-checks --report results/reliability/final.json
python3 scripts/wiring.py --app /private/checkout --out results/reliability/wiring.json
python3 scripts/coverage_check.py
python3 scripts/reliability_compare.py
```

Only automated verification is required. Private source and raw build logs stay private.

### Expanded final result

- Identical expanded suite: **56/57 before → 57/57 after → 57/57 in the separate final run**.
- Whole-app regressions: **65/65 tests passed** (57 GPS and eight map tests), plus source scan, lint and debug assembly.
- Test infrastructure: **19 self-tests passed**; all 14 static integration checks passed and detected their binding removed in memory.
- Four-preference coverage: warning timing 6 runtime / 4 static; lane suppression 10 / 3; map-view/recenter decisions 4 / 5; sensor-assisted heading 12 / 3. Cases can support more than one preference. Static checks do not execute map rendering.
- The newly detected cached-heading reset defect was fixed in private PR #4. Application code stays private; no merge or release is claimed here.

Expanded [private GitHub verification](https://github.com/phuk-prog/drivemate-app/actions/runs/39974699433) passed for candidate `253f0577bb32f9d6d216957aca37a495d9724f2c`: 65 app tests, 19 runner/coverage self-tests, all four preference-evidence gates, source checks, lint and debug assembly.
