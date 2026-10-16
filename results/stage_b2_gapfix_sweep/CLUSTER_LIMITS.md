# Why cluster purity falls at large sigma_cat (analysis of saved data; evaluation labels only)

## Ceiling versus achieved purity (means over 3 seeds)

Ceiling = purity of the best possible rule that sees only the true category block and knows the true category centres (nearest centre), by Monte Carlo from the generator. No clusterer working from the observations can exceed it. Purity grows trivially with the number of clusters, so purities with K = 9-12 are flattered relative to K = 6.

| σ_cat | Ceiling purity | Achieved, discovered K | Achieved, K = 6 (oracle count) | Ceiling − achieved |
|---|---|---|---|---|
| 0.1 | 1.000 | 0.835 | 0.969 | +0.165 |
| 0.4 | 0.994 | 0.930 | 0.942 | +0.063 |
| 0.6 | 0.953 | 0.844 | 0.844 | +0.110 |
| 0.8 | 0.870 | 0.753 | 0.783 | +0.117 |
| 1.0 | 0.773 | 0.684 | 0.696 | +0.089 |
| 1.5 | 0.582 | 0.534 | 0.425 | +0.048 |

## Impure clusters per run (from the 2,500 stored points per run)

| σ_cat | seed | K found | Sample purity | Oracle-K (6) purity | Clusters purity < 0.7 | 0.7-0.9 | ≥ 0.9 | Clusters mixing ≥ 2 categories (each > 20%) | Categories split over ≥ 2 clusters |
|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0 | 5 | 0.843 | 0.999 | 1 | 0 | 4 | 1 | 0 |
| 0.1 | 1 | 5 | 0.848 | 1.000 | 1 | 0 | 4 | 1 | 0 |
| 0.1 | 2 | 5 | 0.836 | 0.907 | 1 | 0 | 4 | 1 | 0 |
| 0.4 | 0 | 6 | 0.974 | 0.967 | 0 | 0 | 6 | 0 | 0 |
| 0.4 | 1 | 6 | 0.985 | 0.990 | 0 | 0 | 6 | 0 | 0 |
| 0.4 | 2 | 5 | 0.834 | 0.868 | 1 | 0 | 4 | 1 | 0 |
| 0.6 | 0 | 6 | 0.861 | 0.849 | 1 | 3 | 2 | 1 | 1 |
| 0.6 | 1 | 6 | 0.831 | 0.835 | 1 | 4 | 1 | 2 | 1 |
| 0.6 | 2 | 6 | 0.849 | 0.848 | 2 | 0 | 4 | 2 | 2 |
| 0.8 | 0 | 11 | 0.771 | 0.787 | 3 | 6 | 2 | 3 | 5 |
| 0.8 | 1 | 12 | 0.751 | 0.769 | 5 | 5 | 2 | 5 | 4 |
| 0.8 | 2 | 9 | 0.745 | 0.794 | 4 | 3 | 2 | 4 | 4 |
| 1.0 | 0 | 10 | 0.695 | 0.714 | 4 | 6 | 0 | 2 | 3 |
| 1.0 | 1 | 10 | 0.652 | 0.691 | 6 | 4 | 0 | 5 | 3 |
| 1.0 | 2 | 12 | 0.703 | 0.684 | 4 | 8 | 0 | 4 | 6 |
| 1.5 | 0 | 9 | 0.545 | 0.390 | 9 | 0 | 0 | 3 | 2 |
| 1.5 | 1 | 10 | 0.533 | 0.413 | 8 | 2 | 0 | 4 | 2 |
| 1.5 | 2 | 10 | 0.535 | 0.471 | 9 | 1 | 0 | 3 | 4 |

## Example cluster compositions, seed 0 (cluster id, share of points, purity, categories above 15% with their share), lowest purity first


**σ_cat 0.8** (K = 11)

| Cluster | Share of points | Purity | Categories (share) |
|---|---|---|---|
| 8 | 0.078 | 0.46 | cat 0: 0.46, cat 5: 0.28 |
| 0 | 0.066 | 0.52 | cat 4: 0.52, cat 5: 0.34 |
| 1 | 0.086 | 0.65 | cat 0: 0.22, cat 5: 0.65 |
| 5 | 0.108 | 0.75 | cat 2: 0.75, cat 5: 0.17 |
| 10 | 0.110 | 0.78 | cat 0: 0.78, cat 5: 0.17 |
| 4 | 0.095 | 0.80 | cat 3: 0.8 |
| 2 | 0.084 | 0.86 | cat 2: 0.86 |
| 9 | 0.122 | 0.87 | cat 4: 0.87 |
| 7 | 0.090 | 0.88 | cat 3: 0.88 |
| 6 | 0.088 | 0.90 | cat 1: 0.9 |
| 3 | 0.072 | 0.90 | cat 1: 0.9 |

**σ_cat 1.0** (K = 10)

| Cluster | Share of points | Purity | Categories (share) |
|---|---|---|---|
| 9 | 0.082 | 0.38 | cat 0: 0.38, cat 4: 0.16, cat 5: 0.26 |
| 1 | 0.095 | 0.59 | cat 0: 0.19, cat 5: 0.59 |
| 5 | 0.120 | 0.62 | cat 2: 0.62, cat 5: 0.22 |
| 7 | 0.108 | 0.69 | cat 3: 0.69 |
| 2 | 0.111 | 0.72 | cat 0: 0.72, cat 5: 0.19 |
| 4 | 0.095 | 0.75 | cat 2: 0.75 |
| 3 | 0.090 | 0.78 | cat 3: 0.78 |
| 0 | 0.130 | 0.79 | cat 4: 0.79 |
| 6 | 0.092 | 0.79 | cat 1: 0.79 |
| 8 | 0.077 | 0.80 | cat 1: 0.8 |

**σ_cat 1.5** (K = 9)

| Cluster | Share of points | Purity | Categories (share) |
|---|---|---|---|
| 1 | 0.087 | 0.34 | cat 0: 0.34, cat 1: 0.17, cat 5: 0.26 |
| 8 | 0.118 | 0.51 | cat 1: 0.24, cat 2: 0.51 |
| 5 | 0.097 | 0.51 | cat 4: 0.16, cat 5: 0.51 |
| 6 | 0.127 | 0.51 | cat 0: 0.16, cat 3: 0.51 |
| 3 | 0.115 | 0.53 | cat 2: 0.53, cat 5: 0.21 |
| 7 | 0.102 | 0.55 | cat 3: 0.55 |
| 0 | 0.116 | 0.58 | cat 0: 0.58, cat 5: 0.16 |
| 4 | 0.128 | 0.64 | cat 4: 0.64 |
| 2 | 0.110 | 0.67 | cat 1: 0.67 |