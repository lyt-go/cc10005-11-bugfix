import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/throttle',
  title: '动态限速管理',
  desc: '管理动态限速规则，根据目标站点响应自动调整请求速率，避免触发反爬机制。',
  entity: '限速规则',
  label: '动态限速',
  columns: [
    '规则编号',
    '目标域组',
    '初始速率',
    '最大速率',
    '加速因子',
    '减速因子',
    '错误率阈值',
    '降速恢复间隔',
  ],
  actions: [
    '提交规则评审',
    '启用规则',
    '关闭规则',
  ],
  statuses: [
    '草稿',
    '规则评审中',
    '已启用',
    '已关闭',
  ],
  stats: [
    { label: '限速规则总数', status: null },
    { label: '已启用规则', status: '已启用' },
    { label: '评审中规则', status: '规则评审中' },
  ],
  keywordField: '规则编号',
  createHint: '限速规则登记入口尚未接入审批流',
  emptyText: '暂无动态限速数据，可先登记限速规则',
})
