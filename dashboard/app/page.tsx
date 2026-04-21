'use client'
import { useEffect, useState } from 'react'
import { NavBar } from '@/components/NavBar'
import { EquityCurve } from '@/components/EquityCurve'
import { SignalGauges } from '@/components/SignalGauges'
import { Positions } from '@/components/Positions'
import { RiskMonitor } from '@/components/RiskMonitor'
import { TradeHistory } from '@/components/TradeHistory'
import { BrainState } from '@/components/BrainState'
import { usePolling } from '@/lib/usePolling'
import { useWebSocket } from '@/lib/useWebSocket'
import { getStatus, getPnL, getPositions, getSignals, getTrades } from '@/lib/api'
import type { StatusData, PnLData, Position, SignalItem, Trade } from '@/lib/types'

const EMPTY_STATUS: StatusData = {
  regime: null, strategy: null, pair: null, signal_score: null,
  last_heartbeat: null, is_running: false, is_paused: false, uptime_seconds: 0,
}
const EMPTY_PNL: PnLData = { equity_curve: [], sharpe: 0, max_drawdown: 0, win_rate: 0, total_pnl: 0 }

export default function Dashboard() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [tick, setTick] = useState(0)

  // 30-second REST polling
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

  // WebSocket real-time overlay
  const wsEvent = useWebSocket()
  const [wsSignals, setWsSignals] = useState<SignalItem[]>([])
  const [newTrade, setNewTrade] = useState<Trade | null>(null)

  useEffect(() => {
    if (!wsEvent) return
    if (wsEvent.type === 'signal_changed') setWsSignals(wsEvent.data)
    if (wsEvent.type === 'trade_executed') setNewTrade(wsEvent.data)
  }, [wsEvent])

  const liveSignals = wsSignals.length > 0 ? wsSignals : signals

  return (
    <div className="dashboard">
      <NavBar status={status} onControlChange={() => setTick(t => t + 1)} />
      <div className="dashboard-grid">
        <div className="area-equity">
          <EquityCurve data={pnl} />
        </div>
        <div className="area-signals">
          <SignalGauges signals={liveSignals} />
        </div>
        <div className="area-positions">
          <Positions positions={positions} />
        </div>
        <div className="area-risk">
          <RiskMonitor status={status} pnl={pnl} />
        </div>
        <div className="area-trades">
          <TradeHistory trades={trades.items} newTrade={newTrade} />
        </div>
        <div className="area-brain">
          <BrainState status={status} signals={liveSignals} />
        </div>
      </div>
    </div>
  )
}
