"""格式转换接口：维护转换器，覆盖提交转换测试、启用转换器、退役转换器等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.formatter import FormatterService

LIST_FIELDS = ["转换器编号", "输入格式", "输出格式", "字段映射表", "日期格式模板", "数值精度", "嵌套展平层数", "空值输出策略"]
STATUSES = ("草稿", "转换测试中", "已启用", "已退役")
ACTIONS = ("提交转换测试", "启用转换器", "退役转换器")

router = build_router(RouterSpec(
    module="formatter",
    tag="格式转换",
    entity="转换器",
    label="格式转换",
    service=FormatterService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按转换器编号检索",
))
