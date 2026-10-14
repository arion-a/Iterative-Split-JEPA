# REPORTING.md — Standard Reporting Format for All Stages

Every stage run, control, and ablation MUST produce a report in this format.
The purpose: anyone reading the report can decide pass/fail without asking
what anything means. Formats below follow the SplitJEPA paper
(arXiv:2610.12349) so our numbers are directly comparable to theirs.

---

## A. Gate table (the decision)

One row per frozen criterion from the stage's config file. Nothing else is a gate.

| Criterion | Plain meaning | Threshold | Measured (mean +/- std over seeds) | Pass? |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Rules: thresholds come from the frozen config only. Anything not in the
config is labeled "informational, not a gate" in a separate table.

## B. Paper-standard metrics (mandatory for every synthetic run)

These six are the paper's accepted metric set (paper Sec 4.1, App C.1).
Definitions are fixed; report all six even if only some are gates.

| Metric | Definition (plain words) | Paper reference value |
|---|---|---|
| Global R^2 | How well a linear readout recovers the COMPLETE true latent from the representation (all methods share the frozen encoder, so this is roughly constant: 0.9977 +/- 0.0016) | ~0.998 |
| Invariant R^2 | Linear readout from the recovered invariant block to the true invariant factors | >= 0.99 at convergence (their script: 0.9980) |
| Variant R^2 | Linear readout from the recovered variant block to the true variant factors | >= 0.99 at convergence |
| Leakage ||A12||_F (normalized /sqrt(d_H)) | How much variant content leaks INTO the invariant block; report normalized form as the paper does for dimension comparisons | ~0.003-0.006 at 30k pairs (harder mixing: 0.0056 +/- 0.0007) |
| Leakage ||A21||_F (normalized /sqrt(d_L)) | How much invariant content leaks into the variant block; the paper's data shows THIS is the sensitive one: 0.156 at 250 pairs, 0.012 at 30k pairs; grows with dimension (0.0053 at d=4 to 0.0325 at d=64) | ~0.012-0.023 at 30k pairs |
| Block purity | 1 - (||A12||^2 + ||A21||^2)/||A||^2 ; 1.0 = perfect separation | near 1.0 |

Reference anchors from the paper (use these to judge "how far from target"):
- Full method at default setting: leakage ~0.003, block R^2 ~0.998.
- WITHOUT the spectral head (= LeJEPA baseline, same frozen encoder):
  invariant/variant R^2 drop and leakage rises to 0.332 +/- 0.215.
  This 0.33 number is the paper's own ablation (Fig 5b-c) — if our no-head
  baseline shows ~0.33, we are exactly reproducing their ablation.
- Coupling-strength sensitivity (their Table 4): at strength 2.0,
  Global R^2 falls to 0.8765 and leakage rises — this is the published
  picture of "encoder missed the identifiable class".
- Efficiency (their Fig 12): time-to-target 3.16 +/- 1.14 s vs V3's
  8.54 +/- 3.05 s; observations 0.307M vs 1.946M; 64 vs 272 parameters.

## C. Standard visual panel (the fixed figures, same every stage)

Every report includes these figures. Names are fixed so you learn them once.

- P1. Gate summary chart — bars for each gated metric with the threshold
  drawn as a horizontal line. (The fastest "are we green" picture.)
- P2. Difference-moment spectrum — eigenvalues of the pair-difference matrix
  in log scale, descending, with the selected block boundary and gap ratio
  annotated. Success looks like: a clear cliff (paper-style gap ratios >10;
  the paper's head-fitting uses exactly this matrix). Failure looks like:
  a flat line (shuffled-pair control) or a cliff at the wrong position
  (rank-deficient variation).
- P3. Ablation bars — four panels in the paper's Fig 5 style:
  full / w-o predictive / w-o invariance / w-o variance. Expected signature
  per the paper: removing predictive hurts Global R^2; removing invariance
  keeps Global R^2 but destroys the blocks (leakage ~0.33); removing
  variance raises covariance error.
- P4. Scaling curves — line plots vs budget, paper Figs 7-11 style:
  x = samples (or steps), y = each metric, our method vs no-head baseline
  vs shuffled control on the same axes. Success looks like: our curves
  flat-and-high; shuffled flat-and-bad; no-head high on Global R^2 but bad
  on block metrics.
- P5. Ladder diagram (our extension; the paper has no equivalent) — the
  nested subspaces: rung-1 variant | rung-2 variant | ... | invariant core,
  with angles and captures annotated. Success looks like: nested boxes with
  angle < 5 deg at every boundary.
- P6. (Robotics stages only) Block-validation bars in the paper's Fig 14
  style: normalized response of r_H vs r_L under viewpoint and trajectory
  pairs. Paper targets: r_L responds 8.4x/14.0x more than r_H to viewpoint,
  2.1x/3.1x to trajectory.

## D. Verdict and controls

- One plain-language verdict line, e.g.:
  "B1 PASSED on 3 seeds: rung-1 angle 0.8-1.2 deg, rung-2 1.3-1.5 deg,
  both inside 5 deg; category core 0.98; gaps 40-53; controls behaved."
- Controls section: each destructive control with its REQUIRED outcome and
  its observed outcome. A gate pass without behaving controls is NOT a pass.
- Informational metrics (not gates) go in a clearly separated table.

## E. Glossary rule

Any term not in the frozen config or this file gets one sentence of plain
definition at first use, flagged "(addition)". No silent new concepts.

## F. Where results live

Raw JSON per run in results/<stage>/<condition>/<seed>.json, the rendered
report as results/<stage>/REPORT.md, one line appended to docs/STATUS.md.
Never overwrite; failed runs are kept and labeled.
