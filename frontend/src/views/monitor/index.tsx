import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/monitor',
  title: '采集监控管理',
  desc: '配置采集运行状态的实时监控面板，对采集量、延迟、错误率和代理健康进行可视化。',
  entity: '监控面板',
  label: '采集监控',
  columns: [
    '面板编号',
    '监控指标集',
    '采样间隔秒',
    '趋势窗口分',
    '异常检测方法',
    '告警触发条件',
    '通知接收组',
    '自动降级开关',
  ],
  actions: [
    '提交面板评审',
    '启用面板',
    '归档面板',
  ],
  statuses: [
    '草稿',
    '面板评审中',
    '已启用',
    '已归档',
  ],
  stats: [
    { label: '监控面板总数', status: null },
    { label: '已启用面板', status: '已启用' },
    { label: '评审中面板', status: '面板评审中' },
  ],
  keywordField: '面板编号',
  createHint: '监控面板登记入口尚未接入审批流',
  emptyText: '暂无采集监控数据，可先登记监控面板',
})
