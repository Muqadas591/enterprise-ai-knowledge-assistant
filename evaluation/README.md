# Retrieval Evaluation

This directory contains the retrieval evaluation dataset and generated results.

## Dataset growth

`datasets/retrieval_eval.json` starts with synthetic enterprise questions across HR, leave, IT security, and expenses. Grow the benchmark progressively to 50, 100, 250, and 500+ representative queries covering HR, Finance, IT, Security, Procurement, Operations, Compliance, policies, and technical documentation.

Each item identifies the source document and the relevant chunk indices. Evaluation runners can use these labels to calculate Recall@1, Recall@3, Recall@5, MRR, and latency.

Generated benchmark output belongs in `results/` and should not be committed unless it is intentionally preserved as a baseline.
