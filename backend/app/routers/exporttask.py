"""数据分发接口：维护分发任务，覆盖提交任务审批、启动分发、取消分发等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.exporttask import ExporttaskService

LIST_FIELDS = ["任务编号", "数据源标识", "目标系统", "传输协议", "压缩格式", "分片大小MB", "加密开关", "校验方式"]
STATUSES = ("草稿", "任务审批中", "执行中", "已完成", "已取消")
ACTIONS = ("提交任务审批", "启动分发", "取消分发")

router = build_router(RouterSpec(
    module="exporttask",
    tag="数据分发",
    entity="分发任务",
    label="数据分发",
    service=ExporttaskService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按任务编号检索",
))
