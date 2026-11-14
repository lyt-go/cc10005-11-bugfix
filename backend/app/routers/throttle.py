"""动态限速接口：维护限速规则，覆盖提交规则评审、启用规则、关闭规则等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.throttle import ThrottleService

LIST_FIELDS = ["规则编号", "目标域组", "初始速率", "最大速率", "加速因子", "减速因子", "错误率阈值", "降速恢复间隔"]
STATUSES = ("草稿", "规则评审中", "已启用", "已关闭")
ACTIONS = ("提交规则评审", "启用规则", "关闭规则")

router = build_router(RouterSpec(
    module="throttle",
    tag="动态限速",
    entity="限速规则",
    label="动态限速",
    service=ThrottleService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按规则编号检索",
))
