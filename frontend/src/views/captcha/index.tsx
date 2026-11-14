import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/captcha',
  title: '验证码处理管理',
  desc: '管理各类型验证码的自动识别与人工打码策略，包括图像验证码、滑块和点击验证。',
  entity: '验证码策略',
  label: '验证码处理',
  columns: [
    '策略编号',
    '验证码类型',
    '识别服务商',
    '识别超时秒',
    '重试次数上限',
    '降级策略',
    '手动打码开关',
    '打码等待队列',
  ],
  actions: [
    '提交策略验证',
    '启用策略',
    '降级策略',
  ],
  statuses: [
    '草稿',
    '策略验证中',
    '已启用',
    '已降级',
  ],
  stats: [
    { label: '验证码策略总数', status: null },
    { label: '已启用策略', status: '已启用' },
    { label: '验证中策略', status: '策略验证中' },
  ],
  keywordField: '策略编号',
  createHint: '验证码策略登记入口尚未接入审批流',
  emptyText: '暂无验证码处理数据，可先登记验证码策略',
})
