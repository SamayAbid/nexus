'use client'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { StatusData, PnLData, Position, SignalItem } from '@/lib/types'

function StatCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '16px 20px',
    }}>
      <div style={{
        fontSize: 10,
        fontWeight: 700,
        letterSpacing: '0.1em',
        color: 'var(--text-3)',
        textTransform: 'uppercase',
        marginBottom: 10,
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 24,
        fontWeight: 700,
        color: color ?? 'var(--text-1)',
        fontFamily: 'var(--font-mono)',
      }}>
        {value}
      </div>
    </div>
  )
}

interface OverviewProps {
  status: StatusData
  pnl: PnLData
  positions: Position[]
  signals: SignalItem[]
}

export function Overview({ status, pnl, positions, signals }: OverviewProps) {
  const totalPnl = pnl.total_pnl
  const pnlColor = totalPnl >= 0 ? 'var(--green)' : 'var(--red)'
  const pnlSign = totalPnl >= 0 ? '+' : ''
  const openPositions = positions.filter(p => p.is_open === 1)

  const btcSignal = signals.find(s => s.pair === 'BTC/USD')
  const composite = btcSignal?.composite ?? 0
  const bias = composite > 0.3 ? 'BULLISH' : composite < -0.3 ? 'BEARISH' : 'NEUTRAL'
  const biasColor = composite > 0.3 ? 'var(--green)' : composite < -0.3 ? 'var(--red)' : 'var(--yellow)'

  const stratLabel =
    status.strategy === 'trend_following' ? 'TREND FOLLOW' :
    status.strategy === 'mean_reversion'  ? 'MEAN REVERT'  :
    status.strategy?.toUpperCase() ?? '—'

  const heartbeat = status.last_heartbeat
    ? new Date(status.last_heartbeat).toLocaleTimeString('en-US', { hour12: false })
    : '—'

  const chartData = pnl.equity_curve.map(p => ({
    t: new Date(p.timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit', hour12: false,
    }),
    v: p.equity,
  }))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        <StatCard
          label="Total P&L"
          value={`${pnlSign}$${Math.abs(totalPnl).toFixed(2)}`}
          color={pnlColor}
        />
        <StatCard
          label="Win Rate"
          value={`${(pnl.win_rate * 100).toFixed(0)}%`}
        />
        <StatCard
          label="Sharpe Ratio"
          value={pnl.sharpe.toFixed(2)}
        />
        <StatCard
          label="Max Drawdown"
          value={`${(pnl.max_drawdown * 100).toFixed(1)}%`}
          color="var(--yellow)"
        />
      </div>

      {/* Equity curve + Agent Brain */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 12 }}>
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '16px 20px',
        }}>
          <div style={{
            fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
            color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: 14,
          }}>
            Equity Curve
          </div>
          {chartData.length === 0 ? (
            <div style={{
              height: 200, display: 'flex', alignItems: 'center',
              justifyContent: 'center', color: 'var(--text-3)', fontSize: 12,
            }}>
              No data yet
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="eq-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#6366F1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="t"
                  tick={{ fill: '#475569', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#475569', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: unknown) => `$${Number(v).toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    fontSize: 11,
                  }}
                  labelStyle={{ color: 'var(--text-2)' }}
                  itemStyle={{ color: '#6366F1', fontFamily: 'var(--font-mono)' }}
                  formatter={(v: unknown) => [`$${Number(v).toFixed(2)}`, 'Equity']}
                />
                <Area
                  type="monotone"
                  dataKey="v"
                  stroke="#6366F1"
                  strokeWidth={2}
                  fill="url(#eq-grad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Agent Brain */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '16px 20px',
          display: 'flex',
          flexDirection: 'column',
          gap: 14,
        }}>
          <div style={{
            fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
            color: 'var(--text-3)', textTransform: 'uppercase',
          }}>
            Agent Brain
          </div>
          {[
            {
              label: 'Regime',
              value: status.regime?.toUpperCase() ?? '—',
              color: status.regime === 'trending' ? 'var(--accent)' : 'var(--cyan)',
            },
            { label: 'Strategy', value: stratLabel },
            { label: 'Bias', value: bias, color: biasColor },
            {
              label: 'Composite',
              value: `${composite >= 0 ? '+' : ''}${composite.toFixed(3)}`,
              color: biasColor,
            },
            {
              label: 'State',
              value: status.is_paused ? 'PAUSED' : 'ACTIVE',
              color: status.is_paused ? 'var(--yellow)' : 'var(--green)',
            },
            { label: 'Last Tick', value: heartbeat },
          ].map(row => (
            <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <span style={{
                fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
                color: 'var(--text-3)', textTransform: 'uppercase',
              }}>
                {row.label}
              </span>
              <span style={{
                fontSize: 14, fontWeight: 600,
                color: row.color ?? 'var(--text-1)',
                fontFamily: 'var(--font-mono)',
              }}>
                {row.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Positions mini-table */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--border)',
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--text-3)', textTransform: 'uppercase',
        }}>
          Open Positions ({openPositions.length})
        </div>
        {openPositions.length === 0 ? (
          <div style={{ padding: '20px 16px', fontSize: 12, color: 'var(--text-3)', textAlign: 'center' }}>
            No open positions
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr>
                {['Pair', 'Direction', 'Entry', 'Size', 'Stop Loss', 'Take Profit'].map(h => (
                  <th key={h} style={{
                    padding: '8px 16px', textAlign: 'left',
                    fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
                    color: 'var(--text-3)', borderBottom: '1px solid var(--border)',
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {openPositions.slice(0, 5).map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{p.pair}</td>
                  <td style={{
                    padding: '9px 16px',
                    color: p.direction === 'long' ? 'var(--green)' : 'var(--red)',
                    fontWeight: 700, textTransform: 'uppercase', fontSize: 11,
                  }}>
                    {p.direction}
                  </td>
                  <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)' }}>{p.entry_price.toFixed(2)}</td>
                  <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)' }}>{p.position_size.toFixed(4)}</td>
                  <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)', color: 'var(--red)' }}>{p.stop_loss.toFixed(2)}</td>
                  <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)', color: 'var(--green)' }}>{p.take_profit.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
