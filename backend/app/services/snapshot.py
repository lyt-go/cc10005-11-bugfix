"""采集快照业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="snapshot",
    entity="数据快照",
    label="采集快照",
    required_fields=("快照编号", "关联任务", "快照时间"),
    status_order=("草稿", "生成中", "已完成", "已过期"),
    action_rules={"生成快照": "生成中", "确认完成": "已完成", "标记过期": "已过期"},
)
class SnapshotService(BaseEntryService):
    spec = SPEC
