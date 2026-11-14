"""种子管理业务规则：状态机、入队去重与爬虫资格联动都收在这里。

种子只能按 草稿→待抓取→抓取中→已完成 推进，中途可废弃；
已废弃、已完成为终态，废弃后不可重新入队。
入队 = 状态校验 + 爬虫资格检查 + 检查点创建，三步一起成功才落账；
同一 URL 在一个队列周期内只有一份活动任务，不同来源、不同标签的
重复种子合并进这份任务，来源与优先级变化写进任务历史。
"""
from __future__ import annotations

from typing import Any, ContextManager

from app.services.base import BaseEntryService, ModuleSpec
from app.services.crawl_runtime import get_runtime

SPEC = ModuleSpec(
    module="seedmgr",
    entity="URL种子",
    label="种子管理",
    required_fields=("种子编号", "种子URL", "发现来源"),
    status_order=("草稿", "待抓取", "抓取中", "已完成", "已废弃"),
    action_rules={"加入队列": "待抓取", "启动抓取": "抓取中", "完成抓取": "已完成", "废弃种子": "已废弃"},
    transitions={
        "加入队列": ("草稿",),
        "启动抓取": ("待抓取",),
        "完成抓取": ("抓取中",),
        "废弃种子": ("草稿", "待抓取", "抓取中"),
    },
    pending_off=("抓取中", "已完成", "已废弃"),
)


class SeedmgrService(BaseEntryService):
    spec = SPEC

    def action_guard(self) -> ContextManager[None]:
        # 入队/启动/完成/废弃都要和抓取队列一起落账，全程在运行时锁内
        return get_runtime().guard()

    def transition_blocked(self, entry: dict[str, Any], action: str) -> str:
        status = entry.get("status")
        if action == "加入队列":
            if status == "已废弃":
                return "已废弃种子不可重新入队"
            if status == "已完成":
                return "已完成种子不可重新入队，如需再次抓取请登记新种子"
            return "种子已在抓取队列中，重复入队已拦截"
        if action == "启动抓取":
            if status == "已废弃":
                return "已废弃种子不可启动抓取"
            if status == "已完成":
                return "已完成种子不可再次启动抓取"
            return "种子尚未入队，请先加入队列"
        if action == "完成抓取":
            return "只有抓取中的种子才能标记完成"
        if action == "废弃种子":
            return f"种子已处于「{status}」状态，不可废弃"
        return super().transition_blocked(entry, action)

    def validate_side_effects(self, entry: dict[str, Any], action: str) -> str | None:
        runtime = get_runtime()
        if action == "加入队列":
            return runtime.check_enqueue()
        if action == "启动抓取":
            return runtime.check_start(entry)
        return None

    def apply_side_effects(self, entry: dict[str, Any], action: str, previous: str) -> str | None:
        runtime = get_runtime()
        if action == "加入队列":
            return runtime.apply_enqueue(entry)
        if action == "启动抓取":
            runtime.apply_start(entry)
        elif action == "完成抓取":
            runtime.apply_finish(entry)
        elif action == "废弃种子":
            runtime.apply_discard(entry)
        return None

    # ---- 核对视图：抓取队列状态、续爬检查点、种子进度 ----
    def queue_status(self) -> list[dict[str, Any]]:
        return get_runtime().queue_snapshot()

    def checkpoints(self) -> list[dict[str, Any]]:
        return get_runtime().checkpoints_snapshot()

    def seed_progress(self, entry_id: int) -> dict[str, Any] | None:
        entry = self.get_entry(entry_id)
        if entry is None:
            return None
        return get_runtime().seed_progress(entry)
