import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/dataclean',
  title: '数据去噪管理',
  desc: '管理采集后数据的去噪清洗规则，包括HTML标签移除、特殊字符过滤和编码纠错。',
  entity: '去噪规则',
  label: '数据去噪',
  columns: [
    '规则编号',
    '目标字段',
    'HTML标签清理',
    '特殊字符过滤',
    '空白规整模式',
    '长度截断阈值',
    '编码纠错',
    '敏感词脱敏',
  ],
  actions: [
    '提交规则验证',
    '启用规则',
    '废弃规则',
  ],
  statuses: [
    '草稿',
    '规则验证中',
    '已启用',
    '已废弃',
  ],
  stats: [
    { label: '去噪规则总数', status: null },
    { label: '已启用规则', status: '已启用' },
    { label: '验证中规则', status: '规则验证中' },
  ],
  keywordField: '规则编号',
  createHint: '去噪规则登记入口尚未接入审批流',
  emptyText: '暂无数据去噪数据，可先登记去噪规则',
})
