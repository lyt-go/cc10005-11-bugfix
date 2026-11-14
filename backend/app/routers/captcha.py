"""验证码处理接口：维护验证码策略，覆盖提交策略验证、启用策略、降级策略等动作。

通用增删查改走 app.routers.common 的统一实现，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.routers.common import RouterSpec, build_router
from app.services.captcha import CaptchaService

LIST_FIELDS = ["策略编号", "验证码类型", "识别服务商", "识别超时秒", "重试次数上限", "降级策略", "手动打码开关", "打码等待队列"]
STATUSES = ("草稿", "策略验证中", "已启用", "已降级")
ACTIONS = ("提交策略验证", "启用策略", "降级策略")

router = build_router(RouterSpec(
    module="captcha",
    tag="验证码处理",
    entity="验证码策略",
    label="验证码处理",
    service=CaptchaService(),
    statuses=STATUSES,
    actions=ACTIONS,
    keyword_desc="按策略编号检索",
))
