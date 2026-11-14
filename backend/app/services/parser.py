"""字段解析器业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="parser",
    entity="解析模板",
    label="字段解析器",
    required_fields=("模板编号", "目标字段数", "XPath表达式"),
    status_order=("草稿", "模板验证中", "已生效", "已废弃"),
    action_rules={"提交模板验证": "模板验证中", "生效模板": "已生效", "废弃模板": "已废弃"},
)
class ParserService(BaseEntryService):
    spec = SPEC
