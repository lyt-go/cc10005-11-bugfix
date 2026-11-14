"""数据去噪接口：维护去噪规则，覆盖提交规则验证、启用规则、废弃规则等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.dataclean import DatacleanService

LIST_FIELDS = ["规则编号", "目标字段", "HTML标签清理", "特殊字符过滤", "空白规整模式", "长度截断阈值", "编码纠错", "敏感词脱敏"]
STATUSES = ("草稿", "规则验证中", "已启用", "已废弃")
ACTIONS = ("提交规则验证", "启用规则", "废弃规则")

router = build_router(RouterSpec(
    module="dataclean",
    tag="数据去噪",
    entity="去噪规则",
    label="数据去噪",
    service=DatacleanService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按规则编号检索",
))
