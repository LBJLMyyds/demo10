# EnAccessMap Melbourne — live demo

A community-reported accessibility map of Melbourne venues, public toilets, and tactile paving, with an automatic
conflict resolution engine for when reports about the same venue disagree. Filterable by step-free entry,
accessible bathroom, seating, and accessible parking — the same four criteria used by
[EnAccess Maps](https://www.enaccessmaps.com), the Melbourne not-for-profit this project's data model follows.

**Live site:** *(add your GitHub Pages URL here once Actions finishes deploying)*

> This repo is a demo/snapshot used to test deployment and showcase the conflict resolution engine. The full
> project — raw data, notebooks, and documentation — lives in the team repository:
> [`lilylin-star/MAST90107-accessibility-map`](https://github.com/lilylin-star/MAST90107-accessibility-map)
> (`Lin-Ma` branch), part of University of Melbourne's MAST90107.

## What's here

```text
frontend/                 Static map app — Leaflet + OpenStreetMap, vanilla HTML/CSS/JS, no build step
  index.html
  assets/app.js
  assets/styles.css
  data/*.json              Generated from accessibility.sqlite — do not hand-edit
database/accessibility.sqlite   Snapshot of the project database (rebuilt from raw data for this package)
export_frontend_data.py   database/accessibility.sqlite -> frontend/data/*.json
src/pipeline/              Full ingestion + cleaning + conflict-resolution pipeline
  build.py                  One-command entrypoint
  clean.py                  Cleaning functions, including build_conflict_candidates() — the engine itself
  config.py, ingest.py, load.py, validate.py
tests/test_conflict_resolution.py   6 unit tests for the conflict resolution engine — all passing
reports/data_validation_report.md   Latest pipeline validation output
docs/
  two_things_tomorrow.md         Short EN prep notes: engine logic + frontend interaction logic
  bilingual_demo_script.md       Full EN/中文 walkthrough + logic script
.github/workflows/deploy-pages.yml   Auto-deploys frontend/ to GitHub Pages on every push to main
```

Raw source CSVs aren't included here (this is a frontend/engine showcase, not the full data pipeline
repository), so running `src/pipeline/build.py` standalone in this repo will fail looking for `data/raw/*.csv`.
`export_frontend_data.py` doesn't have that problem — it only needs the standard library and the committed
`.sqlite` file, so it runs fine on its own here or in CI.

## Running locally

```bash
cd frontend
python3 -m http.server 8000
# open http://localhost:8000 — don't open index.html by double-clicking, browsers
# block the local fetch() calls that load frontend/data/*.json
```

## Regenerating frontend/data/*.json

```bash
python3 export_frontend_data.py
```

Reads `database/accessibility.sqlite` and rewrites `frontend/data/places.json`, `toilets.json`, `tgsi.json`,
`conflicts.json`, and `meta.json`. The GitHub Actions workflow re-runs this automatically on every push to `main`
if the database is present, and falls back to whatever's already committed if it isn't.

## The conflict resolution engine

Every accessibility feature on the map comes from community reports. When reports about the same venue disagree —
one visitor says there's a ramp, another says there isn't — `src/pipeline/clean.py::build_conflict_candidates()`
scores the disagreement and either proposes a value or leaves it for a person:

1. **Only individual review evidence counts.** The venue-level aggregate row is deliberately excluded — it
   summarises the same reviews, so it isn't independent evidence.
2. **Recency-weighted votes.** Each review's weight decays exponentially with age: `2^(-age_days / 180)` — a
   180-day half-life. Recent reports count more, because accessibility features genuinely change over time.
3. **`resolution_score = winner_share × temporal_coverage × certainty`** — how one-sided the result is, how much
   evidence has a usable date, and how much is decisive (yes/no) rather than unsure.
4. Score ≥ 0.75 → **high** evidence quality. Score ≥ 0.60 → **medium**, marked **provisional** with a proposed
   value. Below 0.60 → **low** quality, status **human_review**.

**Real result on the current data — 74 detected conflicts:**

| Status | Count | Share |
|---|---:|---:|
| Provisional (engine proposes a value) | 41 | 55% |
| Human review (left for a person) | 33 | 45% |

Resolution *accuracy* — whether a provisional value actually matches reality — isn't measured yet; that needs a
labelled ground-truth sample that doesn't exist yet (see the team repo's `docs/metric_validation_plan.md`).
Coverage (55%) and human-review-rate (45%), above, don't need ground truth and are computed directly from the
data. The engine's own output notes say plainly: *"the score is heuristic and not calibrated."*

## Where the engine's output shows up in the UI

- The **"Flagged for review"** map layer = venues with an unresolved (`human_review`) conflict, nothing else.
- The venue detail card shows a review banner only for `human_review` conflicts — `provisional` ones don't
  trigger it.
- The **Data Quality** page is the engine's dashboard: stat cards for detected / provisional (with coverage %) /
  human review (with rate %), then a full table where every row shows a status badge, an evidence-quality badge,
  and a specific rationale generated from that row's real numbers — e.g. *"Engine proposes 'no' (high confidence,
  resolution score 85%) — latest evidence 05 Sep 2025."*

## Known data quality notes

Logged automatically in `frontend/data/meta.json` rather than silently fixed — visible on the site's Data Quality
page:

- **95 venues** geocoded outside Victoria (other states, occasionally overseas) — present in the source export
  itself, excluded from the map rather than shown at the wrong location.
- **53 venue names** contain literal `?` characters from a charset mismatch upstream.

## Credits

Data model and filter criteria inspired by [EnAccess Maps](https://www.enaccessmaps.com). Map tiles ©
[OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
