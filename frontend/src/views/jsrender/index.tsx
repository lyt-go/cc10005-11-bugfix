import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/jsrender',
  title: 'JS渲染采集管理',
  desc: '管理需要JavaScript渲染的动态页面采集配置，定义浏览器环境、渲染等待和交互操作。',
  entity: '渲染配置',
  label: 'JS渲染采集',
  columns: [
    '配置编号',
    '目标URL',
    '浏览器类型',
    '渲染等待秒',
    '滚动次数',
    '点击选择器',
    '页面等待条件',
    '截屏开关',
  ],
  actions: [
    '提交渲染测试',
    '标记上线',
    '标记降级',
  ],
  statuses: [
    '草稿',
    '渲染测试中',
    '已上线',
    '已降级',
  ],
  stats: [
    { label: '渲染配置总数', status: null },
    { label: '已上线配置', status: '已上线' },
    { label: '测试中配置', status: '渲染测试中' },
  ],
  keywordField: '配置编号',
  createHint: '渲染配置登记入口尚未接入审批流',
  emptyText: '暂无JS渲染采集数据，可先登记渲染配置',
})
