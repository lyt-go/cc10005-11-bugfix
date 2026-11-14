import { Fragment, useCallback, useEffect, useState } from 'react'

import { request } from '@/api/client'

export type StatSpec = {
  label: string
  /** null 表示总数；'__abnormal__' 表示异常量；其余按状态计数 */
  status: string | null
}

export type ModuleViewConfig = {
  endpoint: string
  title: string
  desc: string
  entity: string
  label: string
  columns: string[]
  actions: string[]
  statuses: string[]
  stats: StatSpec[]
  keywordField: string
  createHint: string
  emptyText: string
  /** seed 表示种子管理，详情抽屉会追加队列状态、检查点与变更历史 */
  detail?: 'seed'
}

type Row = Record<string, string | number | null>

type ActionResult = { ok: boolean; message: string }

type SeedProgress = {
  status?: string
  队列周期?: string
  任务编号?: string
  任务?: Row | null
  检查点?: Row | null
  历史?: Row[]
}

/**
 * 业务模块列表页的统一写法：筛选、统计、动作、详情抽屉。
 * 原本 18 个模块各抄了一遍，动作载荷、查询参数都和后端对不上，
 * 表现为"点不动、旧值残留"；现在交互流程只有这一份。
 */
export function createModuleView(config: ModuleViewConfig) {
  return function ModuleView() {
    const [rows, setRows] = useState<Row[]>([])
    const [total, setTotal] = useState(0)
    const [statValues, setStatValues] = useState<Record<string, number>>({})
    const [errorMessage, setErrorMessage] = useState('')
    const [notice, setNotice] = useState('')
    const [keywordDraft, setKeywordDraft] = useState('')
    const [statusDraft, setStatusDraft] = useState('')
    const [applied, setApplied] = useState({ keyword: '', status: '' })
    const [detail, setDetail] = useState<Row | null>(null)
    const [seedProgress, setSeedProgress] = useState<SeedProgress | null>(null)

    const reload = useCallback(async () => {
      const query = new URLSearchParams()
      if (applied.keyword) query.set('keyword', applied.keyword)
      if (applied.status) query.set('status', applied.status)
      const response = await request(`${config.endpoint}?${query}`)
      if (!response.ok) {
        throw new Error(`${config.label}列表读取失败`)
      }
      const payload = await response.json()
      setRows(payload.items ?? [])
      setTotal(payload.total ?? 0)
    }, [applied])

    const reloadStats = useCallback(async () => {
      const response = await request(`${config.endpoint}/stats`)
      if (!response.ok) {
        return
      }
      const payload = await response.json()
      const values: Record<string, number> = {}
      for (const item of config.stats) {
        if (item.status === null) {
          values[item.label] = Number(payload.total ?? 0)
        } else if (item.status === '__abnormal__') {
          values[item.label] = Number(payload.abnormal ?? 0)
        } else {
          values[item.label] = Number(payload.by_status?.[item.status] ?? 0)
        }
      }
      setStatValues(values)
    }, [])

    const refresh = useCallback(async () => {
      try {
        await Promise.all([reload(), reloadStats()])
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : `${config.label}列表读取失败`)
      }
    }, [reload, reloadStats])

    useEffect(() => {
      void refresh()
    }, [refresh])

    const openDetail = useCallback(async (row: Row) => {
      setErrorMessage('')
      try {
        const response = await request(`${config.endpoint}/${row.id}`)
        if (!response.ok) {
          throw new Error(`${config.entity}详情读取失败`)
        }
        setDetail((await response.json()) as Row)
        if (config.detail === 'seed') {
          const progressRes = await request(`${config.endpoint}/${row.id}/progress`)
          setSeedProgress(progressRes.ok ? ((await progressRes.json()) as SeedProgress) : null)
        } else {
          setSeedProgress(null)
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '详情读取失败')
      }
    }, [])

    async function runAction(action: string, row: Row) {
      setErrorMessage('')
      setNotice('')
      try {
        const response = await request(`${config.endpoint}/${row.id}/actions`, {
          method: 'POST',
          body: JSON.stringify({ values: { action } }),
        })
        const payload = (await response.json().catch(() => null)) as ActionResult | null
        if (!response.ok || !payload || !payload.ok) {
          throw new Error(payload?.message || `${config.label}动作未生效，请稍后重试`)
        }
        setNotice(payload.message)
        await refresh()
        if (detail && detail.id === row.id) {
          await openDetail(row)
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : `${config.label}操作失败`)
      }
    }

    function applyFilters() {
      setErrorMessage('')
      setApplied({ keyword: keywordDraft.trim(), status: statusDraft })
    }

    function resetFilters() {
      setKeywordDraft('')
      setStatusDraft('')
      setApplied({ keyword: '', status: '' })
    }

    return (
      <section className="page" data-module={config.endpoint.split('/').pop()}>
        <header className="page-head">
          <div>
            <h2>{config.title}</h2>
            <p className="page-desc">{config.desc}</p>
          </div>
          <div className="page-actions">
            <button className="btn primary" type="button" onClick={() => setErrorMessage(config.createHint)}>
              登记{config.entity}
            </button>
            <button className="btn" type="button" onClick={() => window.open(`${config.endpoint}/export`, '_blank')}>
              导出{config.label}清单
            </button>
          </div>
        </header>

        <div className="stat-row">
          {config.stats.map((item) => (
            <article key={item.label} className="stat-card">
              <span className="stat-label">{item.label}</span>
              <strong className="stat-value">{statValues[item.label] ?? 0}</strong>
            </article>
          ))}
        </div>

        <form
          className="filter-bar"
          onSubmit={(event) => {
            event.preventDefault()
            applyFilters()
          }}
        >
          <label className="filter-item">
            <span>{config.keywordField}</span>
            <input
              value={keywordDraft}
              placeholder={`按${config.keywordField}检索`}
              onChange={(event) => setKeywordDraft(event.target.value)}
            />
          </label>
          <label className="filter-item">
            <span>状态</span>
            <select value={statusDraft} onChange={(event) => setStatusDraft(event.target.value)}>
              <option value="">全部状态</option>
              {config.statuses.map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </label>
          <button className="btn" type="submit">查询</button>
          <button className="btn ghost" type="button" onClick={resetFilters}>重置条件</button>
        </form>

        <table className="data-table">
          <thead>
            <tr>
              {config.columns.map((column) => <th key={column}>{column}</th>)}
              <th>状态</th>
              <th>可执行动作</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={String(row.id)} data-clickable onClick={() => void openDetail(row)}>
                {config.columns.map((column) => <td key={column}>{row[column] ?? '—'}</td>)}
                <td>{row.status ?? '—'}</td>
                <td className="row-actions" onClick={(event) => event.stopPropagation()}>
                  {config.actions.map((action) => (
                    <button key={action} className="link" type="button" onClick={() => void runAction(action, row)}>
                      {action}
                    </button>
                  ))}
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td className="empty-state" colSpan={config.columns.length + 2}>{config.emptyText}</td>
              </tr>
            )}
          </tbody>
        </table>

        <footer className="page-foot">
          <span>共 {total} 条{config.label}记录</span>
          {notice && <span className="ok-text">{notice}</span>}
          {errorMessage && <span className="error-text">{errorMessage}</span>}
        </footer>

        {detail && (
          <>
            <div className="detail-mask" onClick={() => setDetail(null)} />
            <aside className="detail-panel">
              <header className="detail-head">
                <h3>{config.entity}详情</h3>
                <button className="btn ghost" type="button" onClick={() => setDetail(null)}>关闭</button>
              </header>
              <dl className="detail-grid">
                <dt>ID</dt>
                <dd>{String(detail.id)}</dd>
                <dt>状态</dt>
                <dd>{String(detail.status ?? '—')}</dd>
                {config.columns.map((column) => (
                  <Fragment key={column}>
                    <dt>{column}</dt>
                    <dd>{detail[column] ?? '—'}</dd>
                  </Fragment>
                ))}
                {detail['任务编号'] && (
                  <>
                    <dt>任务编号</dt>
                    <dd>{String(detail['任务编号'])}</dd>
                  </>
                )}
                {detail['队列周期'] && (
                  <>
                    <dt>队列周期</dt>
                    <dd>{String(detail['队列周期'])}</dd>
                  </>
                )}
              </dl>

              {config.detail === 'seed' && seedProgress && (
                <>
                  <section className="detail-section">
                    <h4>抓取队列状态</h4>
                    {seedProgress.任务 ? (
                      <dl className="detail-grid">
                        <dt>任务编号</dt>
                        <dd>{String(seedProgress.任务['任务编号'] ?? '—')}</dd>
                        <dt>任务状态</dt>
                        <dd>{String(seedProgress.任务['状态'] ?? '—')}</dd>
                        <dt>队列周期</dt>
                        <dd>{String(seedProgress.任务['队列周期'] ?? '—')}</dd>
                        <dt>来源列表</dt>
                        <dd>{Array.isArray(seedProgress.任务['来源列表']) ? (seedProgress.任务['来源列表'] as string[]).join('、') : '—'}</dd>
                        <dt>分类标签</dt>
                        <dd>{Array.isArray(seedProgress.任务['分类标签']) ? (seedProgress.任务['分类标签'] as string[]).join('、') : '—'}</dd>
                        <dt>优先级</dt>
                        <dd>{String(seedProgress.任务['优先级'] ?? '—')}</dd>
                      </dl>
                    ) : (
                      <p className="page-desc">尚未入队，没有抓取任务</p>
                    )}
                  </section>
                  <section className="detail-section">
                    <h4>续爬检查点</h4>
                    {seedProgress.检查点 ? (
                      <dl className="detail-grid">
                        <dt>检查点状态</dt>
                        <dd>{String(seedProgress.检查点['状态'] ?? '—')}</dd>
                        <dt>进度</dt>
                        <dd>{String(seedProgress.检查点['进度'] ?? 0)}%</dd>
                        <dt>暂停批次</dt>
                        <dd>{String(seedProgress.检查点['暂停批次'] ?? '—')}</dd>
                        <dt>执行权</dt>
                        <dd>{String(seedProgress.检查点['执行权'] ?? '—')}</dd>
                        <dt>更新时间</dt>
                        <dd>{String(seedProgress.检查点['更新时间'] ?? '—')}</dd>
                      </dl>
                    ) : (
                      <p className="page-desc">暂无检查点</p>
                    )}
                  </section>
                  <section className="detail-section">
                    <h4>变更历史</h4>
                    {seedProgress.历史 && seedProgress.历史.length > 0 ? (
                      <ul className="history-list">
                        {seedProgress.历史.map((item, index) => (
                          <li key={index}>
                            <strong>{String(item['事件'] ?? '')}</strong>
                            <span> · {String(item['时间'] ?? '')}</span>
                            <br />
                            {String(item['详情'] ?? '')}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="page-desc">暂无变更历史</p>
                    )}
                  </section>
                </>
              )}
            </aside>
          </>
        )}
      </section>
    )
  }
}
