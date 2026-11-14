"""JS渲染采集接口：维护渲染配置，覆盖提交渲染测试、标记上线、标记降级等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.jsrender import JsrenderService

LIST_FIELDS = ["配置编号", "目标URL", "浏览器类型", "渲染等待秒", "滚动次数", "点击选择器", "页面等待条件", "截屏开关"]
STATUSES = ("草稿", "渲染测试中", "已上线", "已降级")
ACTIONS = ("提交渲染测试", "标记上线", "标记降级")

router = build_router(RouterSpec(
    module="jsrender",
    tag="JS渲染采集",
    entity="渲染配置",
    label="JS渲染采集",
    service=JsrenderService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按配置编号检索",
))
