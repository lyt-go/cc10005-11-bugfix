"""数据分发业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="exporttask",
    entity="分发任务",
    label="数据分发",
    required_fields=("任务编号", "数据源标识", "目标系统"),
    status_order=("草稿", "任务审批中", "执行中", "已完成", "已取消"),
    action_rules={"提交任务审批": "任务审批中", "启动分发": "执行中", "取消分发": "已取消"},
)
class ExporttaskService(BaseEntryService):
    spec = SPEC
