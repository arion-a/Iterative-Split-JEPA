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

## Stage V: video-first handshake

Plan, checkpoints and results: `docs/IMPLEMENTATION_PLAN.md` (sources in `docs/source/`, binding decisions D13-D32 in `docs/DECISIONS.md`, predictions and outcomes in `docs/EVIDENCE.md`).

```bash
python -c "import yaml; from isj import pendulum_data as p; [p.build(yaml.safe_load(open('configs/handshake.yaml'))['world'], s, f'data/handshake/seed{s}') for s in (0,1,2)]"
python experiments/run_handshake.py --out results/handshake     # P2-P3, ~15 min CPU
python experiments/run_hier.py --out results/hier               # P4
python experiments/run_real.py --out results/real               # P5, needs data/real/morpheus/v{0..9}.mp4 (see configs/real.yaml)
python experiments/build_report.py handshake                    # also: hier, real
pytest -q                                                       # 64 tests
```

New modules: `pendulum.py`, `pendulum_data.py` (generator + sealed audit), `video_io.py`, `video_encoder.py`, `temporal_ladder.py`, `pipeline.py` (discovery side, no physics tokens, enforced by `tests/test_sealed_audit.py`), `quotient_audit.py`, `handshake_eval.py` (evaluator side), `hier.py`, `real_video_io.py`, `real_video.py`.

## Status

See `docs/stage_a_results.md` for the Stage A record. Stage V (video-first handshake) is run: certificate confirmed, naming and seed stability refuted, hierarchical AR world RUNGS 1 (registered 4), real clips informational; the owner's own live capture is the open step.

## The experiment log

* Live page (updated at the end of every step): https://claude.ai/artifact/VtJDac1VU3bgXipNJiKiRE
* Source of truth: `explog/chain.jsonl` (append-only, hash-chained; `python -m isj.explog verify`).
* Rebuild the page: `python experiments/build_log_page.py`, then republish `explog/log_page.html`.
* Stage status (done / next / later) is edited by hand in `explog/stages.json` at the end of each stage.

## Reporting standard and targets

* `docs/REPORTING.md`: the standard report every stage must produce (gate table, the paper's six metrics, fixed figures P1-P6, verdict and controls).
* `docs/TARGETS.md`: how far our numbers are from the paper's.
* `docs/B2.md`, `docs/B2_IMPLEMENTATION.md`: the B2 spec and how it is implemented; results in `results/B2/REPORT.md`.
* `docs/REPORTING_IMPLEMENTATION.md`: what of these is already incorporated, what is missing, and the build order.
