"""连接器管理业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="connector",
    entity="数据连接器",
    label="连接器管理",
    required_fields=("连接器编号", "协议类型", "目标端点"),
    status_order=("草稿", "连通测试中", "已就绪", "已离线"),
    action_rules={"发起连通测试": "连通测试中", "标记就绪": "已就绪", "标记离线": "已离线"},
)
class ConnectorService(BaseEntryService):
    spec = SPEC
