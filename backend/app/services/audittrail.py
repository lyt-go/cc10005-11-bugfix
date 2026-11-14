"""操作审计业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="audittrail",
    entity="审计记录",
    label="操作审计",
    required_fields=("记录编号", "操作类型", "操作对象"),
    status_order=("草稿", "已记录", "已复核"),
    action_rules={"确认记录": "已记录", "提交复核": "已复核"},
)
class AudittrailService(BaseEntryService):
    spec = SPEC
