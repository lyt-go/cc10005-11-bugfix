"""Cookie管理接口：维护会话凭证，覆盖提交验证、标记有效、标记过期等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.cookiejar import CookiejarService

LIST_FIELDS = ["凭证编号", "所属站点", "登录方式", "Cookie内容哈希", "创建时间", "过期时间", "刷新策略", "绑定代理节点"]
STATUSES = ("草稿", "验证中", "有效", "已过期")
ACTIONS = ("提交验证", "标记有效", "标记过期")

router = build_router(RouterSpec(
    module="cookiejar",
    tag="Cookie管理",
    entity="会话凭证",
    label="Cookie管理",
    service=CookiejarService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按凭证编号检索",
))
