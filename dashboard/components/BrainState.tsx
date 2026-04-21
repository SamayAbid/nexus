import type { StatusData, SignalItem } from '@/lib/types'
export function BrainState({ status, signals }: { status: StatusData; signals: SignalItem[] }) {
  return <div className="panel brain-panel"><div className="panel-header"><span className="panel-title">AGENT BRAIN</span></div></div>
}
