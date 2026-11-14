"""采集监控接口：维护监控面板，覆盖提交面板评审、启用面板、归档面板等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.monitor import MonitorService

LIST_FIELDS = ["面板编号", "监控指标集", "采样间隔秒", "趋势窗口分", "异常检测方法", "告警触发条件", "通知接收组", "自动降级开关"]
STATUSES = ("草稿", "面板评审中", "已启用", "已归档")
ACTIONS = ("提交面板评审", "启用面板", "归档面板")

router = build_router(RouterSpec(
    module="monitor",
    tag="采集监控",
    entity="监控面板",
    label="采集监控",
    service=MonitorService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按面板编号检索",
))
