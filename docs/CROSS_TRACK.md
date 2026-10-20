# CROSS_TRACK.md — every certificate against a measured artifact (SYNTHESIS E34, "no orphan theorems"), stage V, 2026-10-20

| Certificate (SYNTHESIS §1) | What was measured in stage V | Artifact | Status |
|---|---|---|---|
| **(S) static** — spectral identification, gap, rank | Gap ratio and S1/S2 per family; variant / invariant R² of each rung against the true blocks | `results/handshake/REPORT.md` (ladder records), `results/hier/REPORT.md` (family records, per-rung R²), `results/e36/*.json` | measured |
| (S) — the full five-gate rung audit (leakage at the permutation null, compression, sufficiency, nesting angle, coarsening) | **not computed** in stage V; nesting holds by construction (hard projection, D9) | — | **orphan, declared** |
| **(D) dynamic** — semiconjugacy | Violation rate V with non-degeneracy (ICC); one-step closure ratio of the core against the full latent; (D) ratio to the oracle-block predictor | handshake report (V, ICC), `results/hier` (D ratio), `results/e36` (closure ratio) | measured; closure gate weakly sensitive (E36) |
| **(C) composition** — rollout, stability | L = Lipschitz constant of the linear transition (D16); K = 8 rollout error; (C) ratio to oracle | handshake report, hier report | measured |
| **(T) transport** — same certificates across nuisance | Nuisance absorbed by the encoder (rendering-pair family ends in S1) and psi's between-release statistic across two renderings (ICC); **not** the NIM probe | handshake ladder records, ICC | partial proxy; **NIM not run in stage V (earlier real-data section only)** |
| **Reach (C6 core)** — horizon grows where D, C hold | Normalised held-out error vs horizon for psi and for the fast block, single level | `results/figures/fig3_reach.svg`, `fig_data.json` | measured for one level; growth **across levels** not tested |
| **Naming (Stage C, evaluator only)** | Spearman(psi, energy) on held-out releases | handshake, scaling reports, `fig2` | 0.786 → 0.970-0.978 with 3× data and 2× steps; 0.99 not reached |
| **Live-data handshake (E44-E47)** | — | — | blocked on the owner's footage |

Reading: (D) and (C) are measured on a discovered coordinate; (S) is measured by gaps and R² but not by the full gate set; (T) is a proxy; the live step is missing. Nothing in stage V claims more than this table shows.
