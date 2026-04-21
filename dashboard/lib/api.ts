import type { StatusData, PnLData, Position, SignalItem, TradesData } from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`${path} → ${res.status}`)
  return res.json() as Promise<T>
}

export const getStatus    = () => get<StatusData>('/api/status')
export const getPnL       = () => get<PnLData>('/api/pnl')
export const getPositions = () => get<Position[]>('/api/positions')
export const getSignals   = () => get<SignalItem[]>('/api/signals')
export const getTrades    = (page = 1) => get<TradesData>(`/api/trades?page=${page}`)

export const postControl = (action: 'pause' | 'resume') =>
  fetch(`${BASE}/api/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  }).then(r => r.json())
