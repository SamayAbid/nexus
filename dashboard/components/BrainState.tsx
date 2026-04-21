'use client'
import type { StatusData, SignalItem } from '@/lib/types'

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="brain-row">
      <span className="brain-label">{label}</span>
      <span className="brain-value" style={color ? { color } : undefined}>{value}</span>
    </div>
  )
}

export function BrainState({ status, signals }: { status: StatusData; signals: SignalItem[] }) {
  const btc = signals.find(s => s.pair === 'BTC/USD')
  const composite = btc?.composite ?? 0

  const bias = composite > 0.3 ? 'BULLISH' : composite < -0.3 ? 'BEARISH' : 'NEUTRAL'
  const biasColor = composite > 0.3 ? 'var(--positive)' : composite < -0.3 ? 'var(--negative)' : 'var(--text-secondary)'

  const stratLabel =
    status.strategy === 'trend_following' ? 'TREND FOLLOW' :
    status.strategy === 'mean_reversion'  ? 'MEAN REVERT'  :
    status.strategy?.toUpperCase() ?? '—'

  const heartbeat = status.last_heartbeat
    ? new Date(status.last_heartbeat).toLocaleTimeString('en-US', { hour12: false })
    : '—'

  return (
    <div className="panel brain-panel">
      <div className="panel-header"><span className="panel-title">AGENT BRAIN</span></div>
      <div className="brain-content">
        <Row label="REGIME"    value={status.regime?.toUpperCase() ?? '—'} color={status.regime === 'trending' ? 'var(--accent)' : '#60A5FA'} />
        <Row label="STRATEGY"  value={stratLabel} />
        <Row label="BIAS"      value={bias} color={biasColor} />
        <Row label="COMPOSITE" value={`${composite >= 0 ? '+' : ''}${composite.toFixed(3)}`} color={biasColor} />
        <Row label="STATE"     value={status.is_paused ? 'PAUSED' : 'ACTIVE'} color={status.is_paused ? 'var(--negative)' : 'var(--positive)'} />
        <Row label="LAST TICK" value={heartbeat} />
      </div>
    </div>
  )
}
