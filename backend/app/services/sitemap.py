"""站点地图业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="sitemap",
    entity="站点描述",
    label="站点地图",
    required_fields=("站点编号", "站点域名", "robots规则"),
    status_order=("草稿", "探测中", "已识别", "已屏蔽"),
    action_rules={"发起探测": "探测中", "确认识别": "已识别", "标记屏蔽": "已屏蔽"},
)
class SitemapService(BaseEntryService):
    spec = SPEC
