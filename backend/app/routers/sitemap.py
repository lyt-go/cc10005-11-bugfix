"""站点地图接口：维护站点描述，覆盖发起探测、确认识别、标记屏蔽等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.sitemap import SitemapService

LIST_FIELDS = ["站点编号", "站点域名", "robots规则", "sitemap地址", "页面模板路径", "翻页参数名", "站点字符编码", "最近探测时间"]
STATUSES = ("草稿", "探测中", "已识别", "已屏蔽")
ACTIONS = ("发起探测", "确认识别", "标记屏蔽")

router = build_router(RouterSpec(
    module="sitemap",
    tag="站点地图",
    entity="站点描述",
    label="站点地图",
    service=SitemapService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按站点编号检索",
))
