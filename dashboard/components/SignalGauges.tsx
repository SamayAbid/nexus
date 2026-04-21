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

interface GaugeProps { label: string; value: number | null; color: string }

function Gauge({ label, value, color }: GaugeProps) {
  const v = value ?? 0
  // Map [-1,+1] to [0, 220] degrees sweep starting at 160°
  const sweep = ((v + 1) / 2) * 220
  const startDeg = 160

  return (
    <div className="gauge-container">
      <svg viewBox="0 0 60 48" className="gauge-svg">
        {/* Track arc */}
        <path
          d={arcPath(30, 34, 22, startDeg, 220)}
          stroke="#1C2333"
          strokeWidth="5"
          fill="none"
          strokeLinecap="round"
        />
        {/* Value arc */}
        {sweep > 2 && (
          <path
            d={arcPath(30, 34, 22, startDeg, sweep)}
            stroke={color}
            strokeWidth="5"
            fill="none"
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 3px ${color}90)` }}
          />
        )}
        {/* Value text */}
        <text
          x="30"
          y="36"
          textAnchor="middle"
          fill={color}
          fontSize="9"
          fontFamily="var(--font-mono)"
          fontWeight="500"
        >
          {v.toFixed(2)}
        </text>
      </svg>
      <span style={{ color, fontSize: 8, fontFamily: 'var(--font-condensed)', fontWeight: 700, letterSpacing: '0.08em', marginTop: -4 }}>
        {label}
      </span>
    </div>
  )
}

const INDICATORS: { key: string; label: string; color: string }[] = [
  { key: 'rsi',       label: 'RSI',   color: '#F59E0B' },
  { key: 'macd',      label: 'MACD',  color: '#34D399' },
  { key: 'vwap',      label: 'VWAP',  color: '#60A5FA' },
  { key: 'bb',        label: 'BB',    color: '#A78BFA' },
  { key: 'composite', label: 'SCORE', color: '#E2E8F0' },
]

export function SignalGauges({ signals }: { signals: SignalItem[] }) {
  const btc = signals.find(s => s.pair === 'BTC/USD')
  const eth = signals.find(s => s.pair === 'ETH/USD')

  return (
    <div className="panel signals-panel">
      <div className="panel-header"><span className="panel-title">SIGNAL GAUGES</span></div>
      <div className="signals-pairs">
        {([['BTC/USD', btc], ['ETH/USD', eth]] as [string, SignalItem | undefined][]).map(([pair, sig]) => (
          <div key={pair} className="signals-pair">
            <span className="pair-label">{pair}</span>
            <div className="gauges-row">
              {INDICATORS.map(ind => (
                <Gauge
                  key={ind.key}
                  label={ind.label}
                  value={(sig?.[ind.key as keyof SignalItem] as number | null | undefined) ?? null}
                  color={ind.color}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
