import type { StatusData, PnLData } from '@/lib/types'
export function RiskMonitor({ status, pnl }: { status: StatusData; pnl: PnLData }) {
  return <div className="panel risk-panel"><div className="panel-header"><span className="panel-title">RISK MONITOR</span></div></div>
}
