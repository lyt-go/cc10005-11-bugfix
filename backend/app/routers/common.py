"""业务模块路由统一写法：列表、统计、导出、登记、详情、动作六件事。

原本 18 个模块各写一遍，且 /export 注册在 /{entry_id} 之后，导出请求被
entry_id 捕获直接 422。现在静态路由先注册、动态路由后注册，六件事只有
这一份实现；各模块的差异收进 RouterSpec。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fastapi import APIRouter, HTTPException, Query

from app.schemas import ActionResult, EntryPayload, PageResult


@dataclass(frozen=True)
class RouterSpec:
    module: str  # 存储表名，也是 API 路径段
    tag: str  # 文档分组，用模块中文名
    entity: str  # 单条记录的中文称呼
    label: str  # 模块中文名
    service: Any  # BaseEntryService 实例
    statuses: tuple[str, ...]
    actions: tuple[str, ...]
    keyword_desc: str
    register_extra: Callable[[APIRouter], None] | None = None  # 模块扩展的静态路由


def build_router(spec: RouterSpec) -> APIRouter:
    router = APIRouter(prefix=f"/api/{spec.module}", tags=[spec.tag])
    service = spec.service
    status_desc = "、".join(spec.statuses)
    action_desc = "、".join(spec.actions)

    @router.get("", response_model=PageResult[dict])
    def list_entries(
        keyword: str | None = Query(default=None, description=spec.keyword_desc),
        status: str | None = Query(default=None, description=status_desc),
        page: int = 1,
        size: int = 20,
    ) -> PageResult[dict]:
        if size > 200:
            raise HTTPException(status_code=400, detail="每页最多 200 条，请缩小分页范围")
        items, total = service.list_entries(keyword=keyword, status=status, page=page, size=size)
        return PageResult(items=items, total=total, page=page, size=size)

    list_entries.__doc__ = f"按编号与状态过滤{spec.label}列表；没有数据时返回空页，不报错。"

    @router.get("/stats")
    def stats() -> dict[str, Any]:
        rows, total = service.list_entries(page=1, size=10000)
        by_status: dict[str, int] = {}
        for row in rows:
            key = str(row.get("status") or "")
            by_status[key] = by_status.get(key, 0) + 1
        abnormal = sum(1 for row in rows if row.get("abnormal"))
        return {"module": spec.module, "total": total, "by_status": by_status, "abnormal": abnormal}

    stats.__doc__ = f"{spec.label}统计：总数、按状态计数与异常量，给看板卡片用。"

    @router.get("/export")
    def export_entries() -> dict[str, Any]:
        items, total = service.list_entries(page=1, size=10000)
        return {"module": spec.module, "total": total, "items": items}

    export_entries.__doc__ = f"导出{spec.label}清单：返回当前过滤条件下的全量数据。"

    # 模块扩展的静态路由（如种子管理的 /queue、/checkpoints）必须排在 /{entry_id} 之前
    if spec.register_extra is not None:
        spec.register_extra(router)

    @router.post("", response_model=ActionResult)
    def create_entry(payload: EntryPayload) -> ActionResult:
        entry, missing = service.create_entry(payload.values)
        if missing:
            return ActionResult(ok=False, message=f"缺少必填字段：{'、'.join(missing)}")
        return ActionResult(ok=True, message=f"{spec.entity}已登记", entry=entry)

    create_entry.__doc__ = f"登记一条{spec.entity}，缺字段时说明原因而不是静默丢弃。"

    @router.get("/{entry_id}", response_model=dict)
    def get_entry(entry_id: int) -> dict:
        entry = service.get_entry(entry_id)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"{spec.entity} {entry_id} 不存在或已归档")
        return entry

    get_entry.__doc__ = f"读取单条{spec.entity}明细；不存在时给出可读的错误说明。"

    @router.post("/{entry_id}/actions", response_model=ActionResult)
    def run_action(entry_id: int, payload: EntryPayload) -> ActionResult:
        action = str(payload.values.get("action") or "").strip()
        entry, message = service.run_action(entry_id, action)
        if entry is None:
            return ActionResult(ok=False, message=message)
        return ActionResult(ok=True, message=message, entry=entry)

    run_action.__doc__ = f"对单条{spec.entity}执行{action_desc}；不允许的动作会被拦下并说明原因。"

    return router
