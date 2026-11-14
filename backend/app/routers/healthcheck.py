"""采集器健康接口：维护健康报告，覆盖生成报告、确认报告、归档报告等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.healthcheck import HealthcheckService

LIST_FIELDS = ["报告编号", "采集器名称", "CPU占用率", "内存占用MB", "网络IO速率", "活跃连接数", "错误队列长度", "检查时间戳"]
STATUSES = ("草稿", "报告中", "已确认", "已归档")
ACTIONS = ("生成报告", "确认报告", "归档报告")

router = build_router(RouterSpec(
    module="healthcheck",
    tag="采集器健康",
    entity="健康报告",
    label="采集器健康",
    service=HealthcheckService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按报告编号检索",
))
