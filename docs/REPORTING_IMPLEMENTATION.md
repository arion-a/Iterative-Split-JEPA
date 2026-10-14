# Incorporating REPORTING.md and TARGETS.md: plan and status

`docs/REPORTING.md` (the standard report format) and `docs/TARGETS.md` (distance to the paper's numbers)
are kept here exactly as written. This file says what is already in place, what is missing, what I found
that needs a decision, and the order I would build it in. Update the status column as things land.

Status: **done** / **partly** / **not yet**.

## 1. Requirement by requirement

| Requirement | Status | Where it stands |
| --- | --- | --- |
| **A. Gate table** from the frozen config only | partly | Frozen criteria exist for Stage A (`configs/stage_a.yaml`) and B1 (`configs/stage_b1.yaml`). B2 has guides, not frozen gates. No generator makes the table yet. See issue 4. |
| **B. Six paper metrics** on every synthetic run | partly | Stage A: all six are stored. B1: per rung, all six (invariant R² is stored as `invariant_content_r2`). Authors' script runs: all six. **B2: not measured** (angle, variant R², core R² only). |
| **C. P1** gate summary chart | not yet | |
| **C. P2** difference-moment spectrum, log scale, boundary and gap ratio annotated | partly | Eigenvalues are stored for every run; the B1 page draws them on a linear scale without the boundary or gap ratio. |
| **C. P3** four-panel ablation bars | partly | Stage A and B1 have the arms (full, no prediction, no spectral head, no regulariser). The "covariance error" measure is not defined or computed. See issue 6. |
| **C. P4** scaling curves vs samples or steps | not yet | No scaling run exists. Needs a pairs-budget sweep (250 to 30,000) for the method, the no-head baseline and shuffled pairs. |
| **C. P5** ladder diagram | not yet | The numbers exist (angles, nesting); the diagram does not. |
| **C. P6** robotics block-validation bars | n/a | No robotics stage yet. |
| **D. Verdict line + controls table** | partly | B1 page has the controls; no one-line verdict in the standard form. |
| **E. Glossary rule** ("(addition)" at first use) | partly | B1 page defines terms; new terms are not flagged "(addition)". |
| **F. Results layout** `results/<stage>/<condition>/<seed>.json`, `results/<stage>/REPORT.md`, one line per run in `docs/STATUS.md`, never overwrite | partly | Runs are write-once but live under `runs/` and are fingerprinted in the log. `docs/STATUS.md` does not exist. See issue 7. |
| **TARGETS table** | partly | Kept as given. Needs the corrections in issues 2 and 3. |

## 2. Where we are against the paper (checked just now, from saved data)

| Quantity | Paper | Ours | Note |
| --- | --- | --- | --- |
| Global R² | 0.9977 | Stage A 0.989; mirror encoder 0.9977; **B1 0.972 ± 0.002** | B1's encoder recovers the 12-number, separate-speed world less well than the paper's 8-number world |
| Invariant R² | 0.998 | Stage A mirror 0.9976; B1 invariant content rung 1 0.980, rung 2 0.979 | |
| Variant R² | about 0.997 | Stage A mirror 0.9977; B1 rung 1 0.956, rung 2 0.982 | rung 1 is the soft spot |
| a12 / a21, raw | 0.003 / 0.024 | Stage A mirror 0.0034 / 0.0231; B1 rung 1 0.041 / 0.024; rung 2 0.027 / 0.011 | the exact match is Stage A only |
| a12 / a21, normalized by the square root of the block size | not stated | B1 rung 1 0.014 / 0.012; rung 2 0.013 / 0.0055 | |
| Block purity | about 0.99993 | B1 0.9998 | |
| No-head baseline, invariant R² / leakage | 0.962 / 0.33 | Stage A mirror 0.9615 / 0.33 (reproduced); **B1 no-head: R² 0.76-0.89, leakage 0.52-0.89** | B1 is a different world, so the 0.33 does not carry over |

## 3. Things I found that need your decision

1. **Raw or normalized leakage.** `REPORTING.md` asks for leakage divided by the square root of the block size. The paper's headline numbers
   (0.003, 0.024, 0.33) match the authors' script in raw form. The "0.012 at 30k pairs" for a21 is the raw 0.0233 divided by 2, so it is
   normalized. I could not verify which convention each paper number uses. **Proposal:** report both, raw and normalized, side by side.
2. **TARGETS says "Our B1 (3 seeds)" but its leakage and no-head rows are Stage A numbers.** B1 has 15 seeds, and B1's own leakage is larger
   (table above). "Matches exactly" holds for Stage A's mirror arm only. **Proposal:** add the B1 rows and label which stage each number is from.
3. **The rung-1 variant R² lever.** `TARGETS.md` suggests more pairs at rung 1 first. B1's global R² is 0.972 against the paper's 0.998, which
   limits every block's R² and may explain the shortfall just as well. **Proposal:** test both with P4: a pairs sweep and a training-steps sweep.
4. **Gates from the frozen config only.** B1's amended leakage floor (0.01, decided after seeing data) is not in the frozen config.
   **Proposal:** add a dated `amendments` block to `configs/stage_b1.yaml` and show both leakage rows in the gate table (original strict rule and
   amended rule), flagged as post hoc.
5. **B2 has no frozen gates and no six-metric set.** **Proposal:** report B2 as informational only, add the six metrics to the B2 code, and rerun
   it (about 10 minutes) so it complies.
6. **"Covariance error" for P3 is undefined.** **Proposal (addition):** the Frobenius norm of the correlation matrix of the frozen encoder output
   minus the identity, divided by the block count. Needs your yes.
7. **`results/` against `runs/`.** Moving existing runs would break the fingerprints in the log. **Proposal:** leave `runs/` as the legacy
   location, copy existing runs into the `results/` layout with an importer, write all new runs to `results/` directly, and start `docs/STATUS.md`
   with one line per existing run set.
8. **Efficiency numbers** (time to target, observation count, parameter count) are not measured. Parameters are 64 for our mirror encoder, as in the paper.
   **Proposal:** record parameters and observations seen as informational; skip time-to-target unless you want it.

## 4. Build order

1. **Done now:** the two files and this plan are on GitHub.
2. `results/` layout, importer for existing runs, `docs/STATUS.md` (small).
3. Reporting module: gate table, six-metric table (raw and normalized), controls table, verdict line, "(addition)" glossary flags (medium).
4. Figures P1, P2 (log scale with boundary and gap ratio), P3, P5 as images that render on GitHub, plus the interactive page (medium).
5. New measurements: B2 six metrics and rerun, covariance error, P4 scaling sweeps (about 20 minutes of computing).
6. Generate `results/stageA|B1|B2/REPORT.md` from existing data and check them against `TARGETS.md`.
