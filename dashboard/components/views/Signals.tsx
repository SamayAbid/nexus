'use client'
import type { SignalItem } from '@/lib/types'

function arcPath(cx: number, cy: number, r: number, startDeg: number, sweepDeg: number): string {
  const toRad = (d: number) => (d - 90) * (Math.PI / 180)
  const s = toRad(startDeg)
  const e = toRad(startDeg + sweepDeg)
  const x1 = cx + r * Math.cos(s)
  const y1 = cy + r * Math.sin(s)
  const x2 = cx + r * Math.cos(e)
  const y2 = cy + r * Math.sin(e)
  const large = sweepDeg > 180 ? 1 : 0
  return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`
}

// value: [-1, +1] range (all signal values are pre-normalized by the agent)
function Gauge({ label, value, color }: { label: string; value: number | null; color: string }) {
  const v = value ?? 0
  const sweep = ((v + 1) / 2) * 220   // map [-1,+1] → [0°, 220°]
  const START = 160                    // arc starts at lower-left

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
      <svg viewBox="0 0 90 90" style={{ width: 90, height: 90, overflow: 'visible' }}>
        {/* Track */}
        <path
          d={arcPath(45, 52, 33, START, 220)}
          stroke="var(--border)"
          strokeWidth="6"
          fill="none"
          strokeLinecap="round"
        />
        {/* Fill */}
        {sweep > 2 && (
          <path
            d={arcPath(45, 52, 33, START, sweep)}
            stroke={color}
            strokeWidth="6"
            fill="none"
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
          />
        )}
        {/* Value text */}
        <text
          x="45" y="50"
          textAnchor="middle"
          dominantBaseline="middle"
          fill={color}
          fontSize="12"
          fontFamily="var(--font-mono)"
          fontWeight="500"
        >
          {v.toFixed(2)}
        </text>
        {/* Indicator label */}
        <text
          x="45" y="65"
          textAnchor="middle"
          fill="var(--text-3)"
          fontSize="9"
          fontFamily="var(--font-sans)"
          fontWeight="700"
          letterSpacing="0.08em"
        >
          {label}
        </text>
      </svg>
    </div>
  )
}

type NumericSignalKey = 'rsi' | 'macd' | 'vwap' | 'bb' | 'composite'

const INDICATORS: { key: NumericSignalKey; label: string; color: string }[] = [
  { key: 'rsi',       label: 'RSI',       color: '#F59E0B' },
  { key: 'macd',      label: 'MACD',      color: '#10B981' },
  { key: 'vwap',      label: 'VWAP',      color: '#60A5FA' },
  { key: 'bb',        label: 'BB',        color: '#A78BFA' },
  { key: 'composite', label: 'COMPOSITE', color: '#F1F5F9' },
]

function PairPanel({ pair, sig }: { pair: string; sig: SignalItem | undefined }) {
  const composite = sig?.composite ?? 0
  const barColor = composite > 0.3 ? 'var(--green)' : composite < -0.3 ? 'var(--red)' : 'var(--yellow)'

  // Composite bar: grows left from center for negative, right for positive
  const barLeft  = composite < 0 ? `${(50 + composite * 50).toFixed(1)}%` : '50%'
  const barWidth = `${Math.abs(composite * 50).toFixed(1)}%`

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '16px 20px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <span style={{
          fontSize: 14, fontWeight: 700,
          fontFamily: 'var(--font-mono)', color: 'var(--text-1)',
        }}>
          {pair}
        </span>
        <span style={{
          fontSize: 12, fontWeight: 600,
          letterSpacing: '0.06em', color: barColor,
          fontFamily: 'var(--font-mono)',
        }}>
          {composite >= 0 ? '+' : ''}{composite.toFixed(3)}
        </span>
      </div>

      <div style={{ display: 'flex', gap: 4 }}>
        {INDICATORS.map(ind => (
          <Gauge
            key={ind.key}
            label={ind.label}
            value={sig?.[ind.key] ?? null}
            color={ind.color}
          />
        ))}
      </div>

      {/* Composite bar */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{
            fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
            color: 'var(--text-3)', textTransform: 'uppercase',
          }}>
            Composite Score
          </span>
          <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: barColor }}>
            {composite.toFixed(3)}
          </span>
        </div>
        <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, position: 'relative' }}>
          {/* Center mark */}
          <div style={{
            position: 'absolute', left: '50%', top: 0, bottom: 0,
            width: 1, background: 'var(--text-3)',
          }} />
          {/* Fill bar */}
          <div style={{
            position: 'absolute',
            left: barLeft,
            width: barWidth,
            height: '100%',
            background: barColor,
            borderRadius: 2,
            transition: 'all 0.5s ease',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
          <span style={{ fontSize: 9, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>-1.0</span>
          <span style={{ fontSize: 9, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>0</span>
          <span style={{ fontSize: 9, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>+1.0</span>
        </div>
      </div>
    </div>
  )
}

export function Signals({ signals }: { signals: SignalItem[] }) {
  const btc = signals.find(s => s.pair === 'BTC/USD')
  const eth = signals.find(s => s.pair === 'ETH/USD')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <PairPanel pair="BTC/USD" sig={btc} />
      <PairPanel pair="ETH/USD" sig={eth} />
    </div>
  )
}
