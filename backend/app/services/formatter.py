"""格式转换业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="formatter",
    entity="转换器",
    label="格式转换",
    required_fields=("转换器编号", "输入格式", "输出格式"),
    status_order=("草稿", "转换测试中", "已启用", "已退役"),
    action_rules={"提交转换测试": "转换测试中", "启用转换器": "已启用", "退役转换器": "已退役"},
)
class FormatterService(BaseEntryService):
    spec = SPEC
