import type { Trade } from '@/lib/types'
export function TradeHistory({ trades, newTrade }: { trades: Trade[]; newTrade: Trade | null }) {
  return <div className="panel trade-panel"><div className="panel-header"><span className="panel-title">TRADE HISTORY</span></div></div>
}
