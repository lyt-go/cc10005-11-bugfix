"""深度爬取接口：维护爬虫配置，覆盖提交策略评审、启用爬取、暂停爬取等动作。

通用增删查改走 app.routers.common 的统一实现；暂停/恢复对抓取队列的联动
在 app.services.deepcrawl 与抓取队列运行时里完成。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.deepcrawl import DeepcrawlService

LIST_FIELDS = ["配置编号", "种子URL", "最大深度", "同域约束", "路径包含规则", "路径排除规则", "并发线程数", "断点续爬"]
STATUSES = ("草稿", "策略评审中", "已启用", "已暂停")
ACTIONS = ("提交策略评审", "启用爬取", "暂停爬取")

router = build_router(RouterSpec(
    module="deepcrawl",
    tag="深度爬取",
    entity="爬虫配置",
    label="深度爬取",
    service=DeepcrawlService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按配置编号检索",
))
