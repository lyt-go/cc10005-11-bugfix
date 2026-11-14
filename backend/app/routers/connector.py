"""连接器管理接口：维护数据连接器，覆盖发起连通测试、标记就绪、标记离线等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.connector import ConnectorService

LIST_FIELDS = ["连接器编号", "协议类型", "目标端点", "认证参数", "重连次数", "心跳间隔", "数据编码", "超时阈值"]
STATUSES = ("草稿", "连通测试中", "已就绪", "已离线")
ACTIONS = ("发起连通测试", "标记就绪", "标记离线")

router = build_router(RouterSpec(
    module="connector",
    tag="连接器管理",
    entity="数据连接器",
    label="连接器管理",
    service=ConnectorService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按连接器编号检索",
))
