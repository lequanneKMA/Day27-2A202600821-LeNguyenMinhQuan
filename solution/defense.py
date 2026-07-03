"""
Your defense. Implement register(ctx) and a handler per event type.
See ../README.md for the full interface + toolkit reference, and
../RULES.md before you start.
"""
from api import Verdict


def register(ctx):
    ctx.on("data_batch", check_data_batch)
    ctx.on("contract_checkpoint", check_contract_checkpoint)
    ctx.on("lineage_run", check_lineage_run)
    ctx.on("feature_materialization", check_feature_materialization)
    ctx.on("embedding_batch", check_embedding_batch)


def check_data_batch(payload, ctx):
    res = ctx.tools.batch_profile(payload["batch_id"])
    if "error" in res:
        return Verdict(alert=False, pillar="checks")
    
    b = ctx.baseline
    if res["row_count"] < b["row_count_min"] or res["row_count"] > b["row_count_max"]:
        return Verdict(alert=True, pillar="checks")
    
    for col, rate in res.get("null_rate", {}).items():
        if rate > b["null_rate_max"]:
            return Verdict(alert=True, pillar="checks")
            
    if res["mean_amount"] < b["mean_amount_min"] or res["mean_amount"] > b["mean_amount_max"]:
        return Verdict(alert=True, pillar="checks")
        
    if res["staleness_min"] > b["staleness_min_max"]:
        return Verdict(alert=True, pillar="checks")
        
    return Verdict(alert=False, pillar="checks")


def check_contract_checkpoint(payload, ctx):
    res = ctx.tools.contract_diff(payload["contract_id"], payload["checkpoint_batch_id"])
    if "error" in res:
        return Verdict(alert=False, pillar="contracts")
        
    if len(res.get("violations", [])) > 0:
        return Verdict(alert=True, pillar="contracts")
        
    b = ctx.baseline
    if res["freshness_delay_min"] > b["freshness_delay_max_min"]:
        return Verdict(alert=True, pillar="contracts")
        
    return Verdict(alert=False, pillar="contracts")


def check_lineage_run(payload, ctx):
    res = ctx.tools.lineage_graph_slice(payload["run_id"])
    if "error" in res:
        return Verdict(alert=False, pillar="lineage")
        
    b = ctx.baseline
    if res["duration_ms"] > b["lineage_duration_ms_max"]:
        return Verdict(alert=True, pillar="lineage")
        
    job = payload.get("job")
    if "lineage_stats" not in ctx.state:
        ctx.state["lineage_stats"] = {}
    
    stats = ctx.state["lineage_stats"].setdefault(job, {"max_up": 0, "max_down": 0})
    actual_up = len(res.get("actual_upstream", []))
    actual_down = res.get("actual_downstream_count", 0)
    
    if actual_up < stats["max_up"]:
        return Verdict(alert=True, pillar="lineage")
    if actual_up > stats["max_up"]:
        stats["max_up"] = actual_up
        
    if actual_down == 0 and stats["max_down"] > 0:
        return Verdict(alert=True, pillar="lineage")
    if actual_down > stats["max_down"]:
        stats["max_down"] = actual_down
        
    return Verdict(alert=False, pillar="lineage")


def check_feature_materialization(payload, ctx):
    res = ctx.tools.feature_drift(payload["feature_view"], payload["batch_id"])
    if "error" in res:
        return Verdict(alert=False, pillar="ai_infra")
        
    b = ctx.baseline
    if res["mean_shift_sigma"] > b["feature_mean_shift_sigma_max"]:
        return Verdict(alert=True, pillar="ai_infra")
        
    return Verdict(alert=False, pillar="ai_infra")


def check_embedding_batch(payload, ctx):
    res = ctx.tools.embedding_drift(payload["corpus"], payload["chunk_batch_id"])
    if "error" in res:
        return Verdict(alert=False, pillar="ai_infra")
        
    b = ctx.baseline
    if res["centroid_shift"] > b["embedding_centroid_shift_max"]:
        return Verdict(alert=True, pillar="ai_infra")
        
    if res["avg_doc_age_days"] > b["corpus_avg_doc_age_days_max"]:
        return Verdict(alert=True, pillar="ai_infra")
        
    return Verdict(alert=False, pillar="ai_infra")
