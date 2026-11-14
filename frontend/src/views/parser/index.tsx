import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/parser',
  title: '字段解析器管理',
  desc: '定义结构化字段的解析模板，组合XPath、正则表达式和类型转换规则。',
  entity: '解析模板',
  label: '字段解析器',
  columns: [
    '模板编号',
    '目标字段数',
    'XPath表达式',
    '正则匹配式',
    '类型转换规则',
    '默认填充值',
    '多值分隔符',
    '嵌套结构深度',
  ],
  actions: [
    '提交模板验证',
    '生效模板',
    '废弃模板',
  ],
  statuses: [
    '草稿',
    '模板验证中',
    '已生效',
    '已废弃',
  ],
  stats: [
    { label: '解析模板总数', status: null },
    { label: '已生效模板', status: '已生效' },
    { label: '验证中模板', status: '模板验证中' },
  ],
  keywordField: '模板编号',
  createHint: '解析模板登记入口尚未接入审批流',
  emptyText: '暂无字段解析器数据，可先登记解析模板',
})
