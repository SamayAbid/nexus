'use client'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { PnLData } from '@/lib/types'

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="stat-box">
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={color ? { color } : undefined}>{value}</span>
    </div>
  )
}

export function EquityCurve({ data }: { data: PnLData }) {
  const { equity_curve, sharpe, max_drawdown, win_rate, total_pnl } = data
  const pnlColor = total_pnl >= 0 ? 'var(--positive)' : 'var(--negative)'

  return (
    <div className="panel equity-panel">
      <div className="panel-header">
        <span className="panel-title">EQUITY CURVE</span>
        <div className="panel-stats">
          <Stat label="TOTAL P&L" value={`${total_pnl >= 0 ? '+' : ''}$${total_pnl.toFixed(2)}`} color={pnlColor} />
          <Stat label="SHARPE" value={sharpe.toFixed(2)} />
          <Stat label="MAX DD" value={`${(max_drawdown * 100).toFixed(1)}%`} color="var(--negative)" />
          <Stat label="WIN RATE" value={`${(win_rate * 100).toFixed(0)}%`} />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={196}>
        <AreaChart data={equity_curve} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="amberFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#F59E0B" stopOpacity={0.18} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
            <filter id="lineGlow" x="-20%" y="-40%" width="140%" height="180%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <XAxis dataKey="timestamp" hide />
          <YAxis domain={['auto', 'auto']} hide />
          <Tooltip
            contentStyle={{
              background: '#0D1017',
              border: '1px solid #1C2333',
              borderRadius: 0,
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
            }}
            labelStyle={{ color: '#64748B' }}
            itemStyle={{ color: '#F59E0B' }}
            formatter={(v: unknown) => {
              const num = typeof v === 'number' ? v : 0
              return [`$${num.toFixed(2)}`, 'Equity']
            }}
          />
          <Area
            type="monotone"
            dataKey="equity"
            stroke="#F59E0B"
            strokeWidth={1.5}
            fill="url(#amberFill)"
            dot={false}
            activeDot={{ r: 3, fill: '#F59E0B', stroke: 'none' }}
            filter="url(#lineGlow)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
