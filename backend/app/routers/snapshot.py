"""采集快照接口：维护数据快照，覆盖生成快照、确认完成、标记过期等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.snapshot import SnapshotService

LIST_FIELDS = ["快照编号", "关联任务", "快照时间", "采集行数", "去重后行数", "新增行数", "变更行数", "快照文件路径"]
STATUSES = ("草稿", "生成中", "已完成", "已过期")
ACTIONS = ("生成快照", "确认完成", "标记过期")

router = build_router(RouterSpec(
    module="snapshot",
    tag="采集快照",
    entity="数据快照",
    label="采集快照",
    service=SnapshotService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按快照编号检索",
))
