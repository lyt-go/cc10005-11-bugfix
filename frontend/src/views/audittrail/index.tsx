import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/audittrail',
  title: '操作审计管理',
  desc: '记录所有数据采集配置的变更操作审计日志，支持变更回溯和合规审查。',
  entity: '审计记录',
  label: '操作审计',
  columns: [
    '记录编号',
    '操作类型',
    '操作对象',
    '操作人',
    '操作时间',
    '操作IP',
    '变更详情',
    '操作结果',
  ],
  actions: [
    '确认记录',
    '提交复核',
  ],
  statuses: [
    '草稿',
    '已记录',
    '已复核',
  ],
  stats: [
    { label: '审计记录总数', status: null },
    { label: '已复核记录', status: '已复核' },
    { label: '今日操作量', status: '已记录' },
  ],
  keywordField: '记录编号',
  createHint: '审计记录登记入口尚未接入审批流',
  emptyText: '暂无操作审计数据，可先登记审计记录',
})
