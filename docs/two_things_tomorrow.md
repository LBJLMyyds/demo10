# Two Things to Explain Tomorrow (v2 — updated for the new engine)

**This replaces the earlier version of this file.** The team pushed an updated conflict resolution engine —
completely different algorithm, different numbers. Use only what's below.

---

## 1. Conflict Resolution Engine — the logic

**What changed since last time:** the engine has been rewritten in `src/pipeline/clean.py`
(`build_conflict_candidates`), directly on `reviews` data — not the three hand-written rules from before. It's a
continuous, weighted scoring approach with its own test suite (`tests/test_conflict_resolution.py`, 6 tests, all
passing).

**How it actually works:**

1. Only **individual review evidence** counts — the venue-level aggregate row is deliberately excluded, because
   it summarises the same reviews and isn't independent evidence. (This also fixes a subtle double-counting issue
   the earlier version had.)
2. Each review's vote gets a **recency weight**: `2^(-age_days / 180)` — an exponential half-life. A review from
   today counts fully; one from 180 days ago counts half as much; one from a year ago counts for very little.
   Undated reviews get no recency weight at all.
3. **resolution_score = winner_share × temporal_coverage × certainty**
   - *winner_share* — how dominant the winning side (yes or no) is among the weighted votes
   - *temporal_coverage* — what fraction of the yes/no evidence actually has a usable date
   - *certainty* — how much of the total weight is decisive (yes/no) rather than unsure
4. Score ≥ 0.75 → **high** evidence quality. Score ≥ 0.60 → **medium**, and the conflict is marked
   **provisional** with a proposed value. Below 0.60 → **low** quality, status **human_review**.

**Real, verified numbers — 74 detected conflicts:**

| Status | Count | Share |
|---|---:|---:|
| Provisional (engine proposes a value) | 41 | 55% |
| Human review (left for a person) | 33 | 45% |

| Evidence quality | Count |
|---|---:|
| High | 11 |
| Medium | 30 |
| Low | 33 |

**The one line that matters if asked "why did the numbers change so much":** the new engine resolves more than
double the share the earlier draft did (55% vs. 23%), because continuous recency-weighted scoring can find a
clear signal in cases a hard 3-tier rule would have thrown out. It's a genuinely better-designed engine — properly
tested, and it fixes a double-counting bug the earlier draft had.

**What's honestly still missing:** resolution *accuracy* — whether a provisional value actually matches reality —
isn't measured yet. That needs a labelled ground-truth sample that doesn't exist yet. Coverage (55%) and
human-review-rate (45%) don't need ground truth and are safe numbers to state confidently. The engine's own notes
field says it directly: *"the score is heuristic and not calibrated."*

---

## 2. Frontend — the interaction logic

**One-sentence architecture:** `database/accessibility.sqlite` → `export_frontend_data.py` (no backend server) →
5 static JSON files → browser fetches them once → everything after that is pure client-side JavaScript + Leaflet.

**The four map layers are independent toggles:** Venues (excludes flagged ones) · Public toilets · Tactile
paving/TGSI (rendered as small dots) · Flagged for review (only venues with a still-unresolved `human_review`
conflict).

**Filtering combines three live signals:** free-text search + category chips (OR) + "must have" feature chips
(AND). Every change re-renders the map, the result list, and the filter counter together.

**Search-to-jump:** Enter or the search icon ranks matches (exact name > starts-with > contains > address
starts-with > address contains) and flies straight to the top result, auto-enabling its layer if it was off.

**Where the engine's output surfaces in the UI:**
- The "Flagged for review" layer = venues with an unresolved conflict, nothing else.
- The detail card shows a review banner only if the venue has a `human_review` conflict — resolved
  (`provisional`) ones don't trigger it.
- The Data Quality page is the engine's dashboard: three stat cards (detected / provisional with coverage % /
  human review with rate %), then a full table where every row shows a status badge, an evidence-quality badge
  (high/medium/low), and a specific one-line rationale built from that row's actual numbers — e.g. *"Engine
  proposes 'no' (high confidence, resolution score 85%) — latest evidence 05 Sep 2025."* That sentence is
  generated per-row from the real score, not a canned string.

---

## If the live site is misbehaving tomorrow

```bash
cd frontend
python3 -m http.server 8000
```

Open `http://localhost:8000`. Guarantees current code, no stale-cache surprises.
