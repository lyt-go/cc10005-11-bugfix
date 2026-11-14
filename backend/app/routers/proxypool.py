"""代理池管理接口：维护代理实例，覆盖提交存活检测、标记可用、回收实例等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.proxypool import ProxypoolService

LIST_FIELDS = ["实例编号", "代理地址", "代理端口", "匿名等级", "出站地域", "响应毫秒", "存活检测时间", "分配权重"]
STATUSES = ("草稿", "存活检测中", "可用", "已回收")
ACTIONS = ("提交存活检测", "标记可用", "回收实例")

router = build_router(RouterSpec(
    module="proxypool",
    tag="代理池管理",
    entity="代理实例",
    label="代理池管理",
    service=ProxypoolService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按实例编号检索",
))
