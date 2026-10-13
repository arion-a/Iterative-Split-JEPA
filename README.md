# Iterative-Split-JEPA

An iteration-based extension of SplitJEPA whose invariant/variant splits are organised
hierarchically (a filtration of predictive invariant layers). This repository is the experimental
harness for the program in the *Experimental Plan* and the *Monograph*.

## Layout

| Path | Contents |
| --- | --- |
| `src/isj/worlds.py` | block-diagonal Gaussian worlds, correspondence families `D_k`, coupling observation map, linear post-prediction representation |
| `src/isj/engine.py` | ZCA whitening, difference moments, descending-order spectral split, gap rule, gauge fix, iterated ladder |
| `src/isj/audits.py` | principal angles, capture, leakage with permutation null + Holm, compression / sufficiency / nesting / rank tests |
| `src/isj/encoder.py` | reconstruction-free encoder training (predictive loss + variance/covariance regulariser) |
| `src/isj/stage_a.py` | Stage A pipeline (trained encoder, frozen) |
| `tests/test_core_linear.py` | the frozen algebraic core (five-block world, four sequential splits, controls, n^-1/2 scaling) |
| `configs/stage_a.yaml` | Stage A configuration; `criteria` block is hash-frozen (`stage_a.criteria.sha256`) |
| `experiments/run_stage_a.py` | runner: 5 seeds x {main, shuffled, 3 ablations}, immutable per-run JSON |
| `runs/` | recorded results (one directory per run set) |

## Run

```bash
pip install -e '.[dev]'
pytest -q                                           # algebraic core (seconds)
python experiments/run_stage_a.py --out runs/stage_a/<tag>   # ~1 min per run on CPU
```

Use `OMP_NUM_THREADS=1` when running several seeds in parallel.

## Status

See `docs/stage_a_results.md` for the Stage A record. Stages B-D are not implemented yet.

## The experiment log

* Live page (updated at the end of every step): https://claude.ai/artifact/VtJDac1VU3bgXipNJiKiRE
* Source of truth: `explog/chain.jsonl` (append-only, hash-chained; `python -m isj.explog verify`).
* Rebuild the page: `python experiments/build_log_page.py`, then republish `explog/log_page.html`.
* Stage status (done / next / later) is edited by hand in `explog/stages.json` at the end of each stage.

## Reporting standard and targets

* `docs/REPORTING.md`: the standard report every stage must produce (gate table, the paper's six metrics, fixed figures P1-P6, verdict and controls).
* `docs/TARGETS.md`: how far our numbers are from the paper's.
* `docs/REPORTING_IMPLEMENTATION.md`: what of these is already incorporated, what is missing, and the build order.
