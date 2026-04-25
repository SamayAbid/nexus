'use client'
import type { StatusData, PnLData, Position, SignalItem } from '@/lib/types'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function Overview(_: { status: StatusData; pnl: PnLData; positions: Position[]; signals: SignalItem[] }) {
  return <div style={{ color: 'var(--text-2)', padding: 20 }}>Overview — coming soon</div>
}
