# Presence versus splitting across E25-E29 (retrospective, descriptive)

Rungs examined: 80 (42 split, 23 not split although the block is at least partly present (presence >= 0.5), 15 absent).

- Lowest presence among rungs that split: **0.966** (n = 42).
- Highest presence among rungs that did not split but are at least partly present: **0.971** (n = 23).
- Reading: when the first number is above the second, presence alone separates split from not split; when they overlap, it does not. The conditional rule (a rung splits when its block presence is at least the threshold AND the previous rung split) is tested below. All of this is read off the data after the fact and is not a criterion; E29 (fresh seeds) tested the unconditional 0.95 version prospectively.

- Rule at presence threshold 0.9: block presence alone explains 74 of 80 rungs; presence AND previous rung split explains 77 of 80.
- Rule at presence threshold 0.95: block presence alone explains 79 of 80 rungs; presence AND previous rung split explains 80 of 80.

| Set | Seed | Rung | Presence of the block (nonlinear probe) | Gap ratio | Angle (deg) | Split |
|---|---|---|---|---|---|---|
| E25 MLP+prediction, speeds 0.2/0.7/0.95 | 30 | 2 | 0.823 | 1.7 | 68.3 | no |
| E25 MLP+prediction, speeds 0.2/0.7/0.95 | 31 | 2 | 0.781 | 4.5 | 86.7 | no |
| E25 MLP+prediction, speeds 0.2/0.7/0.95 | 32 | 2 | 0.741 | 1.4 | 86.9 | no |
| E25 MLP+prediction, speeds 0.2/0.7/0.95 | 33 | 2 | 0.663 | 2.0 | 88.8 | no |
| E25 MLP+prediction, speeds 0.2/0.7/0.95 | 34 | 2 | 0.713 | 1.4 | 74.7 | no |
| E26 MLP+prediction, equal speeds | 30 | 1 | 0.991 | 97.2 | 0.3 | yes |
| E26 MLP+prediction, equal speeds | 30 | 2 | 0.991 | 68.1 | 1.0 | yes |
| E26 MLP+prediction, equal speeds | 31 | 1 | 0.991 | 76.0 | 0.3 | yes |
| E26 MLP+prediction, equal speeds | 31 | 2 | 0.991 | 66.5 | 1.1 | yes |
| E26 MLP+prediction, equal speeds | 32 | 1 | 0.992 | 69.6 | 0.3 | yes |
| E26 MLP+prediction, equal speeds | 32 | 2 | 0.991 | 66.2 | 0.9 | yes |
| E26 MLP+prediction, equal speeds | 33 | 1 | 0.992 | 70.2 | 0.3 | yes |
| E26 MLP+prediction, equal speeds | 33 | 2 | 0.992 | 61.0 | 1.0 | yes |
| E26 MLP+prediction, equal speeds | 34 | 1 | 0.989 | 53.9 | 0.7 | yes |
| E26 MLP+prediction, equal speeds | 34 | 2 | 0.989 | 48.6 | 0.9 | yes |
| E27 mirror+paper | 30 | 1 | 0.997 | 68672.4 | 0.0 | yes |
| E27 mirror+paper | 30 | 2 | 0.997 | 81217.0 | 0.9 | yes |
| E27 mirror+paper | 31 | 1 | 0.997 | 371.4 | 0.1 | yes |
| E27 mirror+paper | 31 | 2 | 0.996 | 745.1 | 0.9 | yes |
| E27 mirror+paper | 32 | 1 | 0.997 | 321.2 | 0.1 | yes |
| E27 mirror+paper | 32 | 2 | 0.995 | 227.4 | 0.9 | yes |
| E27 mirror+paper | 33 | 1 | 0.996 | 207.4 | 0.1 | yes |
| E27 mirror+paper | 33 | 2 | 0.994 | 597.9 | 1.1 | yes |
| E27 mirror+paper | 34 | 1 | 0.997 | 74329.8 | 0.0 | yes |
| E27 mirror+paper | 34 | 2 | 0.997 | 66417.0 | 0.8 | yes |
| E27 mirror+prediction | 30 | 1 | 0.995 | 226.6 | 0.2 | yes |
| E27 mirror+prediction | 30 | 2 | 0.995 | 190.3 | 1.0 | yes |
| E27 mirror+prediction | 31 | 1 | 0.995 | 131.9 | 0.2 | yes |
| E27 mirror+prediction | 31 | 2 | 0.994 | 136.2 | 0.9 | yes |
| E27 mirror+prediction | 32 | 1 | 0.994 | 111.7 | 0.3 | yes |
| E27 mirror+prediction | 32 | 2 | 0.994 | 105.3 | 1.0 | yes |
| E27 mirror+prediction | 33 | 1 | 0.993 | 153.4 | 0.1 | yes |
| E27 mirror+prediction | 33 | 2 | 0.993 | 171.2 | 1.0 | yes |
| E27 mirror+prediction | 34 | 1 | 0.995 | 194.6 | 0.2 | yes |
| E27 mirror+prediction | 34 | 2 | 0.994 | 205.3 | 0.8 | yes |
| E28 MLP+paper, weight 0.01 | 30 | 1 | 0.973 | 80.6 | 0.4 | yes |
| E28 MLP+paper, weight 0.01 | 30 | 2 | 0.973 | 54.4 | 0.8 | yes |
| E28 MLP+paper, weight 0.01 | 31 | 1 | 0.911 | 1.2 | 19.3 | no |
| E28 MLP+paper, weight 0.01 | 31 | 2 | 0.815 | 6.0 | 63.5 | no |
| E28 MLP+paper, weight 0.01 | 32 | 1 | 0.869 | 1.2 | 46.5 | no |
| E28 MLP+paper, weight 0.01 | 32 | 2 | 0.893 | 4.2 | 36.9 | no |
| E28 MLP+paper, weight 0.01 | 33 | 1 | 0.973 | 79.1 | 0.4 | yes |
| E28 MLP+paper, weight 0.01 | 33 | 2 | 0.972 | 52.4 | 0.8 | yes |
| E28 MLP+paper, weight 0.01 | 34 | 1 | 0.897 | 1.7 | 1.6 | no |
| E28 MLP+paper, weight 0.01 | 34 | 2 | 0.890 | 1.3 | 89.1 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 35 | 1 | 0.966 | 24.8 | 1.7 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 35 | 2 | 0.975 | 18.8 | 1.3 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 36 | 1 | 0.972 | 59.1 | 0.4 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 36 | 2 | 0.976 | 43.4 | 1.0 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 37 | 1 | 0.973 | 79.1 | 0.4 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 37 | 2 | 0.974 | 54.5 | 1.2 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 38 | 1 | 0.871 | 1.6 | 1.2 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 38 | 2 | 0.874 | 2.5 | 89.5 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 39 | 1 | 0.974 | 69.1 | 0.3 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 39 | 2 | 0.974 | 48.1 | 1.0 | yes |
| E29 MLP+paper, weight 0.01, fresh seeds | 40 | 1 | 0.943 | 1.5 | 2.6 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 40 | 2 | 0.855 | 1.8 | 86.4 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 41 | 1 | 0.932 | 2.5 | 10.0 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 41 | 2 | 0.971 | 1.6 | 17.2 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 42 | 1 | 0.894 | 1.5 | 55.5 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 42 | 2 | 0.940 | 2.4 | 22.0 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 43 | 1 | 0.850 | 1.6 | 87.8 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 43 | 2 | 0.940 | 2.7 | 17.7 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 44 | 1 | 0.823 | 1.1 | 59.8 | no |
| E29 MLP+paper, weight 0.01, fresh seeds | 44 | 2 | 0.787 | 1.5 | 87.1 | no |
