"""采集监控业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="monitor",
    entity="监控面板",
    label="采集监控",
    required_fields=("面板编号", "监控指标集", "采样间隔秒"),
    status_order=("草稿", "面板评审中", "已启用", "已归档"),
    action_rules={"提交面板评审": "面板评审中", "启用面板": "已启用", "归档面板": "已归档"},
)
class MonitorService(BaseEntryService):
    spec = SPEC
