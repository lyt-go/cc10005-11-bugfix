"""动态限速业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="throttle",
    entity="限速规则",
    label="动态限速",
    required_fields=("规则编号", "目标域组", "初始速率"),
    status_order=("草稿", "规则评审中", "已启用", "已关闭"),
    action_rules={"提交规则评审": "规则评审中", "启用规则": "已启用", "关闭规则": "已关闭"},
)
class ThrottleService(BaseEntryService):
    spec = SPEC
