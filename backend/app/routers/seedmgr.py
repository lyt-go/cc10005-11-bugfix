"""种子管理接口：维护URL种子，覆盖加入队列、启动抓取、完成抓取、废弃种子等动作。

通用增删查改走 app.routers.common 的统一实现；这里额外暴露抓取队列状态、
续爬检查点与种子进度三个核对视图——验证状态机修复不能只看列表状态。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.routers.common import RouterSpec, build_router
from app.services.seedmgr import SeedmgrService

LIST_FIELDS = ["种子编号", "种子URL", "发现来源", "发现时间", "预计数据量", "分类标签", "优先级", "抓取截止日期"]
STATUSES = ("草稿", "待抓取", "抓取中", "已完成", "已废弃")
ACTIONS = ("加入队列", "启动抓取", "完成抓取", "废弃种子")

service = SeedmgrService()


def register_seed_routes(router: APIRouter) -> None:
    @router.get("/queue")
    def queue_status() -> dict:
        """抓取队列状态：每个URL一份活动任务，含队列周期、合并来源与优先级历史。"""
        return {"module": "seedmgr", "items": service.queue_status()}

    @router.get("/checkpoints")
    def checkpoints() -> dict:
        """续爬检查点：进度、暂停批次与执行权归属。"""
        return {"module": "seedmgr", "items": service.checkpoints()}


router = build_router(RouterSpec(
    module="seedmgr",
    tag="种子管理",
    entity="URL种子",
    label="种子管理",
    service=service,
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按种子编号检索",
    register_extra=register_seed_routes,
))


@router.get("/{entry_id}/progress")
def seed_progress(entry_id: int) -> dict:
    """种子进度：当前状态、所属抓取任务、检查点与变更历史。"""
    progress = service.seed_progress(entry_id)
    if progress is None:
        raise HTTPException(status_code=404, detail=f"URL种子 {entry_id} 不存在或已归档")
    return progress
