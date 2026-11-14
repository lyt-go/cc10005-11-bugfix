"""深度爬取业务规则：爬虫配置的启用与暂停直接决定抓取队列可用性。

暂停最后一份已启用配置时，抓取中的种子退回待抓取并冻结检查点；
恢复时按暂停批次认领执行权，并发恢复同一批种子只有一个批次成功。
"""
from __future__ import annotations

from typing import Any, ContextManager

from app.services.base import BaseEntryService, ModuleSpec
from app.services.crawl_runtime import get_runtime

SPEC = ModuleSpec(
    module="deepcrawl",
    entity="爬虫配置",
    label="深度爬取",
    required_fields=("配置编号", "种子URL", "最大深度"),
    status_order=("草稿", "策略评审中", "已启用", "已暂停"),
    action_rules={"提交策略评审": "策略评审中", "启用爬取": "已启用", "暂停爬取": "已暂停"},
    transitions={
        "提交策略评审": ("草稿",),
        "启用爬取": ("策略评审中", "已暂停"),
        "暂停爬取": ("已启用",),
    },
    pending_off=("已启用", "已暂停"),
)


class DeepcrawlService(BaseEntryService):
    spec = SPEC

    def action_guard(self) -> ContextManager[None]:
        # 暂停/恢复要和抓取队列一起落账，全程在运行时锁内
        return get_runtime().guard()

    def transition_blocked(self, entry: dict[str, Any], action: str) -> str:
        status = entry.get("status")
        if action == "暂停爬取":
            return f"爬虫配置当前为「{status}」，只有已启用的配置才能暂停"
        if action == "启用爬取":
            if status == "已启用":
                return "爬虫配置已启用，同一批种子只能由一个批次恢复"
            return f"爬虫配置当前为「{status}」，请先完成策略评审"
        return super().transition_blocked(entry, action)

    def validate_side_effects(self, entry: dict[str, Any], action: str) -> str | None:
        if action == "启用爬取" and entry.get("status") == "已暂停":
            return get_runtime().resume_conflict_check()
        return None

    def apply_side_effects(self, entry: dict[str, Any], action: str, previous: str) -> str | None:
        runtime = get_runtime()
        if action == "暂停爬取":
            paused = runtime.pause_if_unavailable(entry)
            if paused:
                return f"，{paused} 个抓取中的种子已退回待抓取，检查点已冻结"
        if action == "启用爬取" and previous == "已暂停":
            count, token = runtime.claim_resume(entry)
            if count:
                return f"，批次 {token} 取得执行权，{count} 个任务从检查点续爬"
        return None
