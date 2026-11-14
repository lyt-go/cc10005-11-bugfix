"""采集去重接口：维护去重引擎，覆盖提交引擎评估、启用引擎、停用引擎等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.dedupengine import DedupengineService

LIST_FIELDS = ["引擎编号", "去重字段组", "哈希算法", "布隆过滤器大小", "误判容忍率", "滑动窗口天", "跨批次去重", "相似度阈值"]
STATUSES = ("草稿", "引擎评估中", "已启用", "已停用")
ACTIONS = ("提交引擎评估", "启用引擎", "停用引擎")

router = build_router(RouterSpec(
    module="dedupengine",
    tag="采集去重",
    entity="去重引擎",
    label="采集去重",
    service=DedupengineService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按引擎编号检索",
))
