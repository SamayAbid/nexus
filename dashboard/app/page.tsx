'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/Sidebar'
import type { Tab } from '@/components/Sidebar'
import { TopBar } from '@/components/TopBar'
import { Overview } from '@/components/views/Overview'
import { Signals } from '@/components/views/Signals'
import { Positions } from '@/components/views/Positions'
import { Trades } from '@/components/views/Trades'
import { Risk } from '@/components/views/Risk'
import { Control } from '@/components/views/Control'
import { usePolling } from '@/lib/usePolling'
import { useWebSocket } from '@/lib/useWebSocket'
import { getStatus, getPnL, getPositions, getSignals, getTrades } from '@/lib/api'
import type { StatusData, PnLData, Position, SignalItem, Trade } from '@/lib/types'

const EMPTY_STATUS: StatusData = {
  regime: null, strategy: null, pair: null, signal_score: null,
  last_heartbeat: null, is_running: false, is_paused: false, uptime_seconds: 0,
}
const EMPTY_PNL: PnLData = {
  equity_curve: [], sharpe: 0, max_drawdown: 0, win_rate: 0, total_pnl: 0,
}

export default function Dashboard() {
  const VALID_TABS = new Set<Tab>(['overview','signals','positions','trades','risk','control'])

  const [tab, setTab] = useState<Tab>(() => {
    if (typeof window === 'undefined') return 'overview'
    const saved = localStorage.getItem('nexus-tab')
    return (VALID_TABS.has(saved as Tab) ? saved : 'overview') as Tab
  })

  function handleTabChange(t: Tab) {
    setTab(t)
    localStorage.setItem('nexus-tab', t)
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const status    = usePolling(getStatus, 30_000, EMPTY_STATUS)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const pnl       = usePolling(getPnL, 30_000, EMPTY_PNL)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const positions = usePolling(getPositions, 30_000, [] as Position[])
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const signals   = usePolling(getSignals, 30_000, [] as SignalItem[])
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const trades    = usePolling(() => getTrades(1), 30_000, { items: [] as Trade[], total: 0, page: 1, pages: 1 })

  const wsEvent = useWebSocket()
  const [wsSignals, setWsSignals] = useState<SignalItem[]>([])
  // TODO(Task 5): pass newTrade to Trades view to flash new rows
  const [newTrade, setNewTrade] = useState<Trade | null>(null)

  useEffect(() => {
    if (!wsEvent) return
    if (wsEvent.type === 'signal_changed') setWsSignals(wsEvent.data)
    if (wsEvent.type === 'trade_executed') setNewTrade(wsEvent.data)
  }, [wsEvent])

  const liveSignals = wsSignals.length > 0 ? wsSignals : signals

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)' }}>
      <Sidebar
        active={tab}
        onChange={handleTabChange}
        isRunning={status.is_running}
        isPaused={status.is_paused}
      />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
        <TopBar status={status} />
        <main style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
          {tab === 'overview'  && <Overview status={status} pnl={pnl} positions={positions} signals={liveSignals} />}
          {tab === 'signals'   && <Signals signals={liveSignals} />}
          {tab === 'positions' && <Positions positions={positions} />}
          {tab === 'trades'    && <Trades trades={trades} />}
          {tab === 'risk'      && <Risk status={status} pnl={pnl} />}
          {/* TODO(Task 6): onChanged should trigger a status refetch after pause/resume */}
          {tab === 'control'   && <Control status={status} onChanged={() => {}} />}
        </main>
      </div>
    </div>
  )
}
