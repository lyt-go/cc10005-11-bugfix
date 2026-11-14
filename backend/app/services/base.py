"""业务服务统一流程：列表筛选、单条查询、登记与状态流转。

18 个业务模块的读写逻辑原本各抄了一遍，任何调整都要同步改 18 处。
现在收敛成一份：模块差异全部收进 ModuleSpec，流程只有这一份；
有特殊规则的模块（种子管理、深度爬取）通过钩子方法接入抓取队列运行时，
不改动主流程。
"""
from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import Any, ContextManager

from app.store import store


@dataclass(frozen=True)
class ModuleSpec:
    """一个业务模块的全部差异：字段、状态序列、动作表与流转约束。"""

    module: str  # 存储表名，也是 API 路径段
    entity: str  # 单条记录的中文称呼，用于提示文案
    label: str  # 模块中文名，用于动作范围文案
    required_fields: tuple[str, ...]
    status_order: tuple[str, ...]
    action_rules: dict[str, str]
    negative_actions: tuple[str, ...] = ()
    keyword_field: str = ""  # 列表关键字命中的字段，缺省取第一个必填字段
    transitions: dict[str, tuple[str, ...]] = field(default_factory=dict)  # 动作 -> 允许的源状态；缺省不限制
    pending_off: tuple[str, ...] = ()  # 进入这些状态即视为"已处理"，缺省取最后一个状态

    def __post_init__(self) -> None:
        if not self.keyword_field:
            object.__setattr__(self, "keyword_field", self.required_fields[0])
        if not self.pending_off:
            object.__setattr__(self, "pending_off", (self.status_order[-1],))


class BaseEntryService:
    """模块读写的统一流程；子类用钩子接自己的业务规则。"""

    spec: ModuleSpec

    # ---- 列表 / 单条 / 登记：所有模块同一套 ----
    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = store.rows(self.spec.module)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get(self.spec.keyword_field, ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        total = len(rows)
        start = max(page - 1, 0) * size
        return rows[start:start + size], total

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        return store.find(self.spec.module, entry_id)

    def create_entry(self, values: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        missing = [field for field in self.spec.required_fields if not str(values.get(field) or "").strip()]
        if missing:
            return None, missing
        rows = store.rows(self.spec.module)
        entry = {"id": max((int(row.get("id", 0)) for row in rows), default=0) + 1}
        entry.update({field: values.get(field) for field in self.spec.required_fields})
        # 必填之外的字段（如种子的分类标签、优先级）一并保留，后续合并去重要用
        for field, value in values.items():
            if field not in entry:
                entry[field] = value
        entry["status"] = self.spec.status_order[0]
        entry["pending"] = True
        entry["abnormal"] = False
        rows.append(entry)
        return entry, []

    # ---- 状态流转：校验 → 应用 → 联动，在同一保护段里完成 ----
    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]:
        with self.action_guard():
            entry = store.find(self.spec.module, entry_id)
            if entry is None:
                return None, f"{self.spec.entity} {entry_id} 不存在或已归档"
            error = self.validate_action(entry, action)
            if error:
                return None, error
            note = self.apply_action(entry, action)
            return entry, self.success_message(entry, action, note)

    # ---- 以下为可覆写点：默认实现保持各模块既有行为 ----
    def action_guard(self) -> ContextManager[None]:
        """并发保护段：默认无锁；需要跨表原子性的模块返回自己的锁。"""
        return nullcontext()

    def validate_action(self, entry: dict[str, Any], action: str) -> str | None:
        spec = self.spec
        if action not in spec.action_rules:
            return f"动作「{action}」不属于{spec.label}可执行范围"
        target = spec.action_rules[action]
        if target not in spec.status_order:
            return f"目标状态「{target}」不在允许的状态序列里"
        allowed = spec.transitions.get(action)
        if allowed is not None and entry.get("status") not in allowed:
            return self.transition_blocked(entry, action)
        return self.validate_side_effects(entry, action)

    def transition_blocked(self, entry: dict[str, Any], action: str) -> str:
        return f"当前状态「{entry.get('status')}」不允许执行{action}"

    def validate_side_effects(self, entry: dict[str, Any], action: str) -> str | None:
        """联动操作的前置校验，返回 None 表示通过；在 apply 之前调用。"""
        return None

    def apply_action(self, entry: dict[str, Any], action: str) -> str | None:
        spec = self.spec
        previous = str(entry.get("status") or "")
        target = spec.action_rules[action]
        entry["status"] = target
        entry["pending"] = target not in spec.pending_off
        entry["abnormal"] = action in spec.negative_actions
        return self.apply_side_effects(entry, action, previous)

    def apply_side_effects(self, entry: dict[str, Any], action: str, previous: str) -> str | None:
        """联动操作的落账钩子，可返回一段附加说明拼进成功文案。"""
        return None

    def success_message(self, entry: dict[str, Any], action: str, note: str | None) -> str:
        return f"{self.spec.entity}已{action}{note or ''}"
