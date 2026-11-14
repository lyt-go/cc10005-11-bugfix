import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/healthcheck',
  title: '采集器健康管理',
  desc: '监控各采集器节点的运行健康状态，记录资源占用和异常指标。',
  entity: '健康报告',
  label: '采集器健康',
  columns: [
    '报告编号',
    '采集器名称',
    'CPU占用率',
    '内存占用MB',
    '网络IO速率',
    '活跃连接数',
    '错误队列长度',
    '检查时间戳',
  ],
  actions: [
    '生成报告',
    '确认报告',
    '归档报告',
  ],
  statuses: [
    '草稿',
    '报告中',
    '已确认',
    '已归档',
  ],
  stats: [
    { label: '健康报告总数', status: null },
    { label: '已确认报告', status: '已确认' },
    { label: '异常报告数', status: '__abnormal__' },
  ],
  keywordField: '报告编号',
  createHint: '健康报告登记入口尚未接入审批流',
  emptyText: '暂无采集器健康数据，可先登记健康报告',
})
