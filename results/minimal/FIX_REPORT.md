# E45: whitening scale fixed (plain sums), 4 and 5 blocks; frozen criteria `configs/fix.criteria.yaml`

**E45: CONFIRMED**

## 4 blocks: rung line met, health line met, core line met
After the fix (10 seeds): clean rungs by rung index [9, 9, 10] (needs 7); output covariance healthy (min eigenvalue at least 0.5) on 10 (needs 9); last-block presence at least 0.95 on 9 (needs 7). Before the fix (E44, same seeds): clean rungs [9, 8, 9]; healthy on 3; core present on 0.

| Seed | Angles per rung | Gap ratios | Presence per block | Min output-covariance eigenvalue |
|---|---|---|---|---|
| 160 | 0.9, 1.7, 1.8 | 83, 63, 97 | 0.85, 0.91, 0.94, 0.97 | 0.919 |
| 161 | 0.8, 1.4, 1.2 | 74, 65, 95 | 0.88, 0.93, 0.94, 0.97 | 0.922 |
| 162 | 0.9, 1.3, 1.7 | 81, 69, 96 | 0.89, 0.90, 0.93, 0.97 | 0.914 |
| 163 | 1.0, 1.3, 1.5 | 76, 64, 91 | 0.86, 0.88, 0.94, 0.97 | 0.925 |
| 164 | 1.2, 71.0, 2.3 | 63, 62, 88 | 0.92, 0.70, 0.94, 0.97 | 0.923 |
| 165 | 0.8, 1.4, 1.3 | 79, 69, 92 | 0.83, 0.89, 0.92, 0.97 | 0.922 |
| 166 | 1.4, 1.6, 2.0 | 79, 57, 53 | 0.86, 0.91, 0.93, 0.73 | 0.914 |
| 167 | 83.6, 1.5, 1.9 | 98, 49, 92 | 0.66, 0.92, 0.93, 0.97 | 0.920 |
| 168 | 0.7, 1.3, 1.8 | 78, 64, 98 | 0.90, 0.91, 0.93, 0.96 | 0.927 |
| 169 | 1.3, 1.4, 1.7 | 74, 62, 90 | 0.88, 0.91, 0.93, 0.96 | 0.925 |

## 5 blocks: rung line met, health line met, core line met
After the fix (10 seeds): clean rungs by rung index [10, 10, 10, 10] (needs 7); output covariance healthy (min eigenvalue at least 0.5) on 10 (needs 9); last-block presence at least 0.95 on 10 (needs 7). Before the fix (E44, same seeds): clean rungs [9, 9, 7, 7]; healthy on 0; core present on 0.

| Seed | Angles per rung | Gap ratios | Presence per block | Min output-covariance eigenvalue |
|---|---|---|---|---|
| 160 | 0.8, 1.5, 1.3, 1.7 | 66, 54, 60, 80 | 0.95, 0.95, 0.93, 0.97, 0.98 | 0.905 |
| 161 | 4.0, 1.4, 2.0, 1.6 | 56, 49, 56, 68 | 0.76, 0.94, 0.95, 0.96, 0.98 | 0.902 |
| 162 | 0.7, 1.3, 1.7, 2.1 | 73, 59, 51, 76 | 0.91, 0.93, 0.95, 0.95, 0.98 | 0.905 |
| 163 | 0.8, 1.8, 1.8, 1.6 | 72, 43, 52, 77 | 0.92, 0.95, 0.96, 0.96, 0.98 | 0.904 |
| 164 | 0.8, 1.3, 1.7, 2.0 | 79, 65, 58, 78 | 0.88, 0.93, 0.93, 0.96, 0.98 | 0.907 |
| 165 | 0.9, 4.2, 1.2, 1.8 | 110, 52, 64, 82 | 0.86, 0.73, 0.94, 0.94, 0.98 | 0.913 |
| 166 | 0.9, 1.0, 1.4, 1.7 | 93, 65, 57, 78 | 0.93, 0.93, 0.95, 0.95, 0.99 | 0.898 |
| 167 | 1.8, 1.2, 1.7, 2.1 | 67, 48, 60, 83 | 0.83, 0.94, 0.95, 0.95, 0.96 | 0.908 |
| 168 | 1.0, 0.9, 1.3, 1.9 | 56, 50, 53, 73 | 0.93, 0.94, 0.94, 0.96, 0.98 | 0.903 |
| 169 | 0.7, 1.2, 1.5, 1.5 | 76, 52, 49, 83 | 0.93, 0.94, 0.95, 0.96, 0.98 | 0.917 |

