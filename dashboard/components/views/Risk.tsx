'use client'
import type { StatusData, PnLData } from '@/lib/types'

function ProgressBar({ label, value, max, color }: {
  label: string; value: number; max: number; color: string
}) {
  const pct = Math.min((Math.abs(value) / max) * 100, 100)
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
          color: 'var(--text-3)', textTransform: 'uppercase',
        }}>
          {label}
        </span>
        <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color }}>
          {value >= 0 ? '+' : ''}{value.toFixed(1)}%
        </span>
      </div>
      <div style={{ height: 6, background: 'var(--border)', borderRadius: 3 }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: color, borderRadius: 3,
          transition: 'width 0.5s ease',
        }} />
      </div>
    </div>
  )
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '10px 0', borderBottom: '1px solid var(--border)',
    }}>
      <span style={{
        fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
        color: 'var(--text-3)', textTransform: 'uppercase',
      }}>
        {label}
      </span>
      <span style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-1)', fontWeight: 600 }}>
        {value}
      </span>
    </div>
  )
}

export function Risk({ status, pnl }: { status: StatusData; pnl: PnLData }) {
  const dailyPct    = (pnl.total_pnl / 10000) * 100
  const drawdownPct = pnl.max_drawdown * 100
  const hours = Math.floor(status.uptime_seconds / 3600)
  const mins  = Math.floor((status.uptime_seconds % 3600) / 60)

  const rules = [
    { label: 'Max daily loss',   value: '3%',         ok: Math.abs(dailyPct) < 3 },
    { label: 'Max drawdown',     value: '10%',        ok: drawdownPct < 10 },
    { label: 'Position limit',   value: '2 per pair', ok: true },
    { label: 'Min signal score', value: '0.35',       ok: true },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Circuit breaker banner */}
      {status.is_paused && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid var(--red)',
          borderRadius: 8,
          padding: '14px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          <span style={{ fontSize: 20 }}>⚡</span>
          <div>
            <div style={{
              fontSize: 13, fontWeight: 700, color: 'var(--red)',
              letterSpacing: '0.08em', textTransform: 'uppercase',
            }}>
              Circuit Breaker Active
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-2)', marginTop: 3 }}>
              Agent is paused. Navigate to Control tab to resume.
            </div>
          </div>
        </div>
      )}

      {/* Risk bars */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '16px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: 18,
      }}>
        <div style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--text-3)', textTransform: 'uppercase',
        }}>
          Risk Exposure
        </div>
        <ProgressBar
          label="Daily P&L"
          value={dailyPct}
          max={5}
          color={dailyPct >= 0 ? 'var(--green)' : 'var(--red)'}
        />
        <ProgressBar
          label="Max Drawdown"
          value={-drawdownPct}
          max={10}
          color="var(--yellow)"
        />
      </div>

      {/* Performance */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '16px 20px',
      }}>
        <div style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: 4,
        }}>
          Performance
        </div>
        <MetricRow label="Win Rate"     value={`${(pnl.win_rate * 100).toFixed(0)}%`} />
        <MetricRow label="Sharpe Ratio" value={pnl.sharpe.toFixed(2)} />
        <MetricRow label="Max Drawdown" value={`${drawdownPct.toFixed(1)}%`} />
        <MetricRow label="Total P&L"    value={`${pnl.total_pnl >= 0 ? '+' : ''}$${pnl.total_pnl.toFixed(2)}`} />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 10 }}>
          <span style={{
            fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
            color: 'var(--text-3)', textTransform: 'uppercase',
          }}>
            Uptime
          </span>
          <span style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-1)', fontWeight: 600 }}>
            {hours}h {mins}m
          </span>
        </div>
      </div>

      {/* Risk rules grid */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '16px 20px',
      }}>
        <div style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: 12,
        }}>
          Risk Rules
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {rules.map(rule => (
            <div key={rule.label} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '10px 12px',
              background: 'var(--bg)',
              borderRadius: 6,
              border: `1px solid ${rule.ok ? 'var(--border)' : 'var(--red)'}`,
            }}>
              <span style={{ fontSize: 11, color: 'var(--text-2)' }}>{rule.label}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-1)' }}>
                  {rule.value}
                </span>
                <span style={{ fontSize: 13, color: rule.ok ? 'var(--green)' : 'var(--red)' }}>
                  {rule.ok ? '✓' : '✗'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
