import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/connector',
  title: '连接器管理管理',
  desc: '管理各类数据源的连接器配置，支持HTTP、数据库、消息队列等多种协议的统一接入。',
  entity: '数据连接器',
  label: '连接器管理',
  columns: [
    '连接器编号',
    '协议类型',
    '目标端点',
    '认证参数',
    '重连次数',
    '心跳间隔',
    '数据编码',
    '超时阈值',
  ],
  actions: [
    '发起连通测试',
    '标记就绪',
    '标记离线',
  ],
  statuses: [
    '草稿',
    '连通测试中',
    '已就绪',
    '已离线',
  ],
  stats: [
    { label: '连接器总数', status: null },
    { label: '已就绪连接器', status: '已就绪' },
    { label: '测试中连接器', status: '连通测试中' },
  ],
  keywordField: '连接器编号',
  createHint: '数据连接器登记入口尚未接入审批流',
  emptyText: '暂无连接器管理数据，可先登记数据连接器',
})
