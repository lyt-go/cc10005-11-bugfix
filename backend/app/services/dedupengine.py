"""采集去重业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="dedupengine",
    entity="去重引擎",
    label="采集去重",
    required_fields=("引擎编号", "去重字段组", "哈希算法"),
    status_order=("草稿", "引擎评估中", "已启用", "已停用"),
    action_rules={"提交引擎评估": "引擎评估中", "启用引擎": "已启用", "停用引擎": "已停用"},
    negative_actions=("停用引擎",),
)
class DedupengineService(BaseEntryService):
    spec = SPEC
