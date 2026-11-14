import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/dedupengine',
  title: '采集去重管理',
  desc: '管理采集数据的去重引擎配置，支持精确去重、模糊去重和跨批次去重策略。',
  entity: '去重引擎',
  label: '采集去重',
  columns: [
    '引擎编号',
    '去重字段组',
    '哈希算法',
    '布隆过滤器大小',
    '误判容忍率',
    '滑动窗口天',
    '跨批次去重',
    '相似度阈值',
  ],
  actions: [
    '提交引擎评估',
    '启用引擎',
    '停用引擎',
  ],
  statuses: [
    '草稿',
    '引擎评估中',
    '已启用',
    '已停用',
  ],
  stats: [
    { label: '去重引擎总数', status: null },
    { label: '已启用引擎', status: '已启用' },
    { label: '评估中引擎', status: '引擎评估中' },
  ],
  keywordField: '引擎编号',
  createHint: '去重引擎登记入口尚未接入审批流',
  emptyText: '暂无采集去重数据，可先登记去重引擎',
})
