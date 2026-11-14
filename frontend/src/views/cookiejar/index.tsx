import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/cookiejar',
  title: 'Cookie管理管理',
  desc: '管理爬虫登录会话的Cookie凭证，跟踪有效期和自动刷新策略。',
  entity: '会话凭证',
  label: 'Cookie管理',
  columns: [
    '凭证编号',
    '所属站点',
    '登录方式',
    'Cookie内容哈希',
    '创建时间',
    '过期时间',
    '刷新策略',
    '绑定代理节点',
  ],
  actions: [
    '提交验证',
    '标记有效',
    '标记过期',
  ],
  statuses: [
    '草稿',
    '验证中',
    '有效',
    '已过期',
  ],
  stats: [
    { label: '会话凭证总数', status: null },
    { label: '有效凭证数', status: '有效' },
    { label: '已过期凭证数', status: '已过期' },
  ],
  keywordField: '凭证编号',
  createHint: '会话凭证登记入口尚未接入审批流',
  emptyText: '暂无Cookie管理数据，可先登记会话凭证',
})
