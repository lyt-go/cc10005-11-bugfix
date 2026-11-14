"""代理池管理业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="proxypool",
    entity="代理实例",
    label="代理池管理",
    required_fields=("实例编号", "代理地址", "代理端口"),
    status_order=("草稿", "存活检测中", "可用", "已回收"),
    action_rules={"提交存活检测": "存活检测中", "标记可用": "可用", "回收实例": "已回收"},
)
class ProxypoolService(BaseEntryService):
    spec = SPEC
