import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/proxypool',
  title: '代理池管理管理',
  desc: '管理动态代理池，维护代理的可用性检测、地域分布和负载均衡调度。',
  entity: '代理实例',
  label: '代理池管理',
  columns: [
    '实例编号',
    '代理地址',
    '代理端口',
    '匿名等级',
    '出站地域',
    '响应毫秒',
    '存活检测时间',
    '分配权重',
  ],
  actions: [
    '提交存活检测',
    '标记可用',
    '回收实例',
  ],
  statuses: [
    '草稿',
    '存活检测中',
    '可用',
    '已回收',
  ],
  stats: [
    { label: '代理实例总数', status: null },
    { label: '可用实例数', status: '可用' },
    { label: '检测中实例数', status: '存活检测中' },
  ],
  keywordField: '实例编号',
  createHint: '代理实例登记入口尚未接入审批流',
  emptyText: '暂无代理池管理数据，可先登记代理实例',
})
