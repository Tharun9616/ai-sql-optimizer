| Method | Avg Execution Time | Plan Accuracy |
|---|---:|---:|
| Full Scan | 16.12 ms | N/A |
| Rule Based | 17.25 ms | 80.8% |
| AI Optimizer | 17.18 ms | 83.3% |
| Oracle (best possible) | 14.25 ms | 100.0% |

Random Forest on 240 held-out queries: accuracy 0.833, precision 0.877, recall 0.866, F1 0.872

Feature importance
- index_selectivity: 0.489
- selectivity: 0.357
- log_rows: 0.053
- n_indexed: 0.037
- has_equality: 0.036
- n_conditions: 0.028
