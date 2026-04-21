'use client'
import type { StatusData, PnLData } from '@/lib/types'

function Bar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min((Math.abs(value) / max) * 100, 100)
  return (
    <div className="risk-bar-row">
      <span className="risk-bar-label">{label}</span>
      <div className="risk-bar-track">
        <div className="risk-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="risk-bar-value">{value >= 0 ? '+' : ''}{value.toFixed(1)}%</span>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="risk-metric">
      <span className="risk-metric-label">{label}</span>
      <span className="risk-metric-value">{value}</span>
    </div>
  )
}

export function RiskMonitor({ status, pnl }: { status: StatusData; pnl: PnLData }) {
  const dailyPct = (pnl.total_pnl / 10000) * 100
  const hours = Math.floor(status.uptime_seconds / 3600)
  const mins  = Math.floor((status.uptime_seconds % 3600) / 60)

  return (
    <div className="panel risk-panel">
      <div className="panel-header">
        <span className="panel-title">RISK MONITOR</span>
        {status.is_paused && <span className="circuit-breaker-badge">⚡ CB ACTIVE</span>}
      </div>
      <div className="risk-content">
        <Bar
          label="DAILY P&L"
          value={dailyPct}
          max={5}
          color={dailyPct >= 0 ? 'var(--positive)' : 'var(--negative)'}
        />
        <Bar
          label="MAX DRAWDOWN"
          value={pnl.max_drawdown * 100}
          max={10}
          color="var(--accent)"
        />
        <Metric label="WIN RATE" value={`${(pnl.win_rate * 100).toFixed(0)}%`} />
        <Metric label="SHARPE" value={pnl.sharpe.toFixed(2)} />
        <Metric label="UPTIME" value={`${hours}h ${mins}m`} />
      </div>
    </div>
  )
}
