"""数据去噪业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="dataclean",
    entity="去噪规则",
    label="数据去噪",
    required_fields=("规则编号", "目标字段", "HTML标签清理"),
    status_order=("草稿", "规则验证中", "已启用", "已废弃"),
    action_rules={"提交规则验证": "规则验证中", "启用规则": "已启用", "废弃规则": "已废弃"},
)
class DatacleanService(BaseEntryService):
    spec = SPEC
