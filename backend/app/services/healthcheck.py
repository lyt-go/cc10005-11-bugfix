"""采集器健康业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="healthcheck",
    entity="健康报告",
    label="采集器健康",
    required_fields=("报告编号", "采集器名称", "CPU占用率"),
    status_order=("草稿", "报告中", "已确认", "已归档"),
    action_rules={"生成报告": "报告中", "确认报告": "已确认", "归档报告": "已归档"},
)
class HealthcheckService(BaseEntryService):
    spec = SPEC
