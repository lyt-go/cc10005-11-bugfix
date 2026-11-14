"""Cookie管理业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="cookiejar",
    entity="会话凭证",
    label="Cookie管理",
    required_fields=("凭证编号", "所属站点", "登录方式"),
    status_order=("草稿", "验证中", "有效", "已过期"),
    action_rules={"提交验证": "验证中", "标记有效": "有效", "标记过期": "已过期"},
)
class CookiejarService(BaseEntryService):
    spec = SPEC
