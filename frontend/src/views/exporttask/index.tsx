import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/exporttask',
  title: '数据分发管理',
  desc: '管理采集结果的分发投递任务，支持多地推送、压缩加密和完整性校验。',
  entity: '分发任务',
  label: '数据分发',
  columns: [
    '任务编号',
    '数据源标识',
    '目标系统',
    '传输协议',
    '压缩格式',
    '分片大小MB',
    '加密开关',
    '校验方式',
  ],
  actions: [
    '提交任务审批',
    '启动分发',
    '取消分发',
  ],
  statuses: [
    '草稿',
    '任务审批中',
    '执行中',
    '已完成',
    '已取消',
  ],
  stats: [
    { label: '分发任务总数', status: null },
    { label: '执行中任务', status: '执行中' },
    { label: '已完成任务', status: '已完成' },
  ],
  keywordField: '任务编号',
  createHint: '分发任务登记入口尚未接入审批流',
  emptyText: '暂无数据分发数据，可先登记分发任务',
})
