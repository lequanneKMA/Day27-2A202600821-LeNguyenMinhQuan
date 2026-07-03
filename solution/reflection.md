# Reflection (≤1 page)

**Which fault types were hardest to catch, and why?**

The `lineage` faults (specifically `missing_upstream` and `orphan_output`) were the hardest to catch. Unlike data quality issues or embedding drift, these faults could not be detected using a static threshold from the provided baseline. To successfully identify them, it was necessary to maintain state across events using `ctx.state`. By tracking the maximum number of upstream edges and downstream consumers seen for each specific job, we essentially built a dynamic, localized baseline that allowed us to detect when an expected dependency went missing or an output was orphaned in subsequent runs.

**What would you change about your cost/coverage tradeoff, if you had another pass?**

Our current implementation aggressively calls the corresponding metered tool for every single event. While this maximizes the True Positive Rate (TPR) and works well within the practice budget (spending 180 out of 220 credits), it would likely result in cost overage penalties if the event volume increases or the budget tightens. In another pass, I would implement adaptive sampling based on `ctx.tools.budget_remaining()`. For instance, we could probabilistically sample events (e.g., skipping checks on `data_batch` if the previous 10 batches were pristine) or chain our checks (only running the expensive `feature_drift` check if upstream `data_batch` anomalies were detected or skipping it for very frequent feature views). This would preserve our budget for higher-risk or more anomalous events.
