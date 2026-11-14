import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/formatter',
  title: '格式转换管理',
  desc: '管理采集数据的格式转换规则，支持JSON、CSV、XML、Parquet等格式间的互转。',
  entity: '转换器',
  label: '格式转换',
  columns: [
    '转换器编号',
    '输入格式',
    '输出格式',
    '字段映射表',
    '日期格式模板',
    '数值精度',
    '嵌套展平层数',
    '空值输出策略',
  ],
  actions: [
    '提交转换测试',
    '启用转换器',
    '退役转换器',
  ],
  statuses: [
    '草稿',
    '转换测试中',
    '已启用',
    '已退役',
  ],
  stats: [
    { label: '转换器总数', status: null },
    { label: '已启用转换器', status: '已启用' },
    { label: '测试中转换器', status: '转换测试中' },
  ],
  keywordField: '转换器编号',
  createHint: '转换器登记入口尚未接入审批流',
  emptyText: '暂无格式转换数据，可先登记转换器',
})
