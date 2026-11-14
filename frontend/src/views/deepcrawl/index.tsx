import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/deepcrawl',
  title: '深度爬取管理',
  desc: '管理网站深度爬取配置，定义种子入口、深度边界、路径过滤和断点续爬策略。',
  entity: '爬虫配置',
  label: '深度爬取',
  columns: [
    '配置编号',
    '种子URL',
    '最大深度',
    '同域约束',
    '路径包含规则',
    '路径排除规则',
    '并发线程数',
    '断点续爬',
  ],
  actions: [
    '提交策略评审',
    '启用爬取',
    '暂停爬取',
  ],
  statuses: [
    '草稿',
    '策略评审中',
    '已启用',
    '已暂停',
  ],
  stats: [
    { label: '爬虫配置总数', status: null },
    { label: '已启用配置', status: '已启用' },
    { label: '评审中配置', status: '策略评审中' },
  ],
  keywordField: '配置编号',
  createHint: '爬虫配置登记入口尚未接入审批流',
  emptyText: '暂无深度爬取数据，可先登记爬虫配置',
})
