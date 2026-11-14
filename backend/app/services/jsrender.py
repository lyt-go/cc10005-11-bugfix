"""JS渲染采集业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="jsrender",
    entity="渲染配置",
    label="JS渲染采集",
    required_fields=("配置编号", "目标URL", "浏览器类型"),
    status_order=("草稿", "渲染测试中", "已上线", "已降级"),
    action_rules={"提交渲染测试": "渲染测试中", "标记上线": "已上线", "标记降级": "已降级"},
)
class JsrenderService(BaseEntryService):
    spec = SPEC
