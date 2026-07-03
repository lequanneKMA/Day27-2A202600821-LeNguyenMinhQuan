# Reflection (≤1 page)

**Which fault types were hardest to catch, and why?**

The hardest faults were the subtle data-quality and AI-infra shifts that sat well inside the published 3-sigma baseline limits. Static thresholding caught the obvious failures but missed too many lower-magnitude private faults. I moved row-count and mean-amount checks to an inferred 1.5-sigma band, lowered null-rate, staleness, AI drift, and lineage-runtime thresholds, and kept the structural lineage logic stateful by tracking the largest upstream and downstream shapes seen per job.

**What would you change about your cost/coverage tradeoff, if you had another pass?**

The main tradeoff is false positives versus private-phase recall. Public favored a more conservative detector, but private faults were smaller and the FPR penalty was still cheaper than missing many faults. The final version calls the relevant tool for each event, accepts more false alarms, and uses calibrated lower thresholds to improve private TPR while staying within budget.
