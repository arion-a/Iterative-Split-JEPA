# E20 blind check: recalibrated gap criterion on fresh seeds 3-5 (σ_cat 0.4 and 0.6)

**Owner's prediction** (cluster-built gap clears 0.6 × the perfect-cluster gap on every seed at both noise levels, B2 + Tier 1): **NOT confirmed**. σ 0.4: B2 + Tier 1 meets it on 3/3, untreated on 1/3; σ 0.6: B2 + Tier 1 meets it on 1/3, untreated on 1/3.

**Corrected contamination model (informational, v_cat frozen at 2.14):** median relative error 0.24 (limit 0.25) -> **PASSES**.

| σ_cat | seed | Cluster purity | K found | True ρ | Gap B1 twins | Achievable gap (perfect clusters) | Gap B2 untreated (ratio) | Gap B2 + Tier 1 (ratio) | Untreated meets | Tier 1 meets | Model-predicted untreated gap | Model relative error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.4 | 3 | 0.836 | 5 | 0.220 | 37.8 | 4.91 | 3.43 (0.70) | 3.72 (0.76) | yes | yes | 2.15 | 0.37 |
| 0.4 | 4 | 0.933 | 9 | 0.104 | 33.7 | 5.00 | 2.39 (0.48) | 3.08 (0.62) | no | yes | 3.08 | 0.29 |
| 0.4 | 5 | 0.834 | 5 | 0.185 | 31.2 | 5.32 | 2.39 (0.45) | 3.63 (0.68) | no | yes | 2.41 | 0.01 |
| 0.6 | 3 | 0.823 | 6 | 0.271 | 50.7 | 3.12 | 1.89 (0.61) | 1.98 (0.64) | yes | yes | 1.54 | 0.19 |
| 0.6 | 4 | 0.853 | 8 | 0.215 | 42.9 | 3.17 | 1.30 (0.41) | 1.56 (0.49) | no | no | 1.74 | 0.34 |
| 0.6 | 5 | 0.821 | 11 | 0.245 | 37.9 | 3.13 | 1.34 (0.43) | 1.42 (0.45) | no | no | 1.59 | 0.19 |