import type { SignalItem } from '@/lib/types'
export function SignalGauges({ signals }: { signals: SignalItem[] }) {
  return <div className="panel signals-panel"><div className="panel-header"><span className="panel-title">SIGNAL GAUGES</span></div></div>
}
