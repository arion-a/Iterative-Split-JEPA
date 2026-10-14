# Decision policy (decide-don't-ask)

Reconstructed on 2026-10-13T22:35Z from the owner's instruction message, because the file named there was not in the repository.
Owner: please replace this with your original if it differs.

* Human-approved tasks proceed without further questions. When a choice is needed, decide it, and log a line starting `DECIDE:` in the
  experiment log (explog) and, if it changes a rule, in `docs/DECISIONS.md`.
* A DECIDE line states: what was decided, the alternatives considered, and why.
* Pre-registered predictions (`docs/EVIDENCE.md`) are written before the run and never edited afterwards. If a prediction is refuted, that is a
  first-class result: report it as refuted with the numbers, do not tune parameters to fit, and register any follow-up as a new prediction.
* Results are never overwritten. New runs go to new directories.
