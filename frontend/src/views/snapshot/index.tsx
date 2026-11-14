import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/snapshot',
  title: '采集快照管理',
  desc: '管理每次采集的数据快照记录，追踪增量采集的新增与变更数据量。',
  entity: '数据快照',
  label: '采集快照',
  columns: [
    '快照编号',
    '关联任务',
    '快照时间',
    '采集行数',
    '去重后行数',
    '新增行数',
    '变更行数',
    '快照文件路径',
  ],
  actions: [
    '生成快照',
    '确认完成',
    '标记过期',
  ],
  statuses: [
    '草稿',
    '生成中',
    '已完成',
    '已过期',
  ],
  stats: [
    { label: '数据快照总数', status: null },
    { label: '已完成快照', status: '已完成' },
    { label: '本月采集量', status: '生成中' },
  ],
  keywordField: '快照编号',
  createHint: '数据快照登记入口尚未接入审批流',
  emptyText: '暂无采集快照数据，可先登记数据快照',
})
