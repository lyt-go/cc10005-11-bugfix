"""操作审计接口：维护审计记录，覆盖确认记录、提交复核等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.audittrail import AudittrailService

LIST_FIELDS = ["记录编号", "操作类型", "操作对象", "操作人", "操作时间", "操作IP", "变更详情", "操作结果"]
STATUSES = ("草稿", "已记录", "已复核")
ACTIONS = ("确认记录", "提交复核")

router = build_router(RouterSpec(
    module="audittrail",
    tag="操作审计",
    entity="审计记录",
    label="操作审计",
    service=AudittrailService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按记录编号检索",
))
