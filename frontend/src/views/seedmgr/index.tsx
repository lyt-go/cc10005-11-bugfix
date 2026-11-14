import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/seedmgr',
  title: '种子管理管理',
  desc: '管理待爬取的URL种子库，维护种子的发现途径、优先级和分类标签。',
  entity: 'URL种子',
  label: '种子管理',
  columns: [
    '种子编号',
    '种子URL',
    '发现来源',
    '发现时间',
    '预计数据量',
    '分类标签',
    '优先级',
    '抓取截止日期',
  ],
  actions: [
    '加入队列',
    '启动抓取',
    '完成抓取',
    '废弃种子',
  ],
  statuses: [
    '草稿',
    '待抓取',
    '抓取中',
    '已完成',
    '已废弃',
  ],
  stats: [
    { label: 'URL种子总数', status: null },
    { label: '待抓取种子', status: '待抓取' },
    { label: '抓取中种子', status: '抓取中' },
  ],
  keywordField: '种子编号',
  createHint: 'URL种子登记入口尚未接入审批流',
  emptyText: '暂无种子管理数据，可先登记URL种子',
  detail: 'seed',
})
