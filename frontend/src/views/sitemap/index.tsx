import { createModuleView } from '../ModuleView'

export default createModuleView({
  endpoint: '/api/sitemap',
  title: '站点地图管理',
  desc: '维护目标站点的结构描述信息，记录robots规则、站点地图和页面模板路径。',
  entity: '站点描述',
  label: '站点地图',
  columns: [
    '站点编号',
    '站点域名',
    'robots规则',
    'sitemap地址',
    '页面模板路径',
    '翻页参数名',
    '站点字符编码',
    '最近探测时间',
  ],
  actions: [
    '发起探测',
    '确认识别',
    '标记屏蔽',
  ],
  statuses: [
    '草稿',
    '探测中',
    '已识别',
    '已屏蔽',
  ],
  stats: [
    { label: '站点描述总数', status: null },
    { label: '已识别站点', status: '已识别' },
    { label: '探测中站点', status: '探测中' },
  ],
  keywordField: '站点编号',
  createHint: '站点描述登记入口尚未接入审批流',
  emptyText: '暂无站点地图数据，可先登记站点描述',
})
