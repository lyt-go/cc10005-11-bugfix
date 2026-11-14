"""字段解析器接口：维护解析模板，覆盖提交模板验证、生效模板、废弃模板等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.parser import ParserService

LIST_FIELDS = ["模板编号", "目标字段数", "XPath表达式", "正则匹配式", "类型转换规则", "默认填充值", "多值分隔符", "嵌套结构深度"]
STATUSES = ("草稿", "模板验证中", "已生效", "已废弃")
ACTIONS = ("提交模板验证", "生效模板", "废弃模板")

router = build_router(RouterSpec(
    module="parser",
    tag="字段解析器",
    entity="解析模板",
    label="字段解析器",
    service=ParserService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按模板编号检索",
))
