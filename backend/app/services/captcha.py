"""验证码处理业务规则：状态流转、字段校验与筛选口径都收在这里。

流程与口径统一在 app.services.base，这里只登记本模块的差异配置。
"""
from __future__ import annotations

from app.services.base import BaseEntryService, ModuleSpec

SPEC = ModuleSpec(
    module="captcha",
    entity="验证码策略",
    label="验证码处理",
    required_fields=("策略编号", "验证码类型", "识别服务商"),
    status_order=("草稿", "策略验证中", "已启用", "已降级"),
    action_rules={"提交策略验证": "策略验证中", "启用策略": "已启用", "降级策略": "已降级"},
)
class CaptchaService(BaseEntryService):
    spec = SPEC
