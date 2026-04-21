'use client'
import { useMemo } from 'react'
import type { Trade } from '@/lib/types'

function TradeRow({ trade, isNew }: { trade: Trade; isNew: boolean }) {
  const time = new Date(trade.timestamp).toLocaleTimeString('en-US', {
    hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
  const stratLabel = trade.strategy === 'trend_following' ? 'TREND' : 'MR'
  return (
    <div className={`trade-row${isNew ? ' new' : ''}`}>
      <span className="trade-time">{time}</span>
      <span className="trade-pair">{trade.pair}</span>
      <span className={`trade-action ${trade.action}`}>{trade.action.toUpperCase()}</span>
      <span className="trade-strategy">{stratLabel}</span>
      <span className="trade-score" style={{ color: trade.signal_score >= 0 ? 'var(--positive)' : 'var(--negative)' }}>
        {trade.signal_score >= 0 ? '+' : ''}{trade.signal_score.toFixed(2)}
      </span>
      <span className={`trade-outcome ${trade.outcome ?? 'open'}`}>
        {(trade.outcome ?? 'OPEN').toUpperCase()}
      </span>
    </div>
  )
}

export function TradeHistory({ trades, newTrade }: { trades: Trade[]; newTrade: Trade | null }) {
  const all = useMemo(() => {
    if (newTrade && !trades.find(t => t.id === newTrade.id)) {
      return [newTrade, ...trades]
    }
    return trades
  }, [trades, newTrade])

  return (
    <div className="panel trade-panel">
      <div className="panel-header">
        <span className="panel-title">TRADE HISTORY</span>
        <span style={{ fontSize: 10, color: 'var(--text-secondary)', fontFamily: 'var(--font-condensed)' }}>
          {all.length} TRADES
        </span>
      </div>
      <div className="trade-header-row">
        {['TIME', 'PAIR', 'DIR', 'STRAT', 'SCORE', 'STATUS'].map(h => (
          <span key={h}>{h}</span>
        ))}
      </div>
      <div className="trade-feed">
        {all.length === 0 ? (
          <div className="empty-state">NO TRADES YET</div>
        ) : (
          all.slice(0, 100).map(t => (
            <TradeRow key={t.id} trade={t} isNew={newTrade?.id === t.id} />
          ))
        )}
      </div>
    </div>
  )
}
