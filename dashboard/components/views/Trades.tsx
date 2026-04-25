'use client'
import { useState } from 'react'
import type { TradesData } from '@/lib/types'
import { getTrades } from '@/lib/api'

function pageBtnStyle(disabled: boolean): React.CSSProperties {
  return {
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 4,
    color: disabled ? 'var(--text-3)' : 'var(--text-2)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    padding: '4px 10px',
    fontSize: 14,
    opacity: disabled ? 0.4 : 1,
  }
}

export function Trades({ trades }: { trades: TradesData }) {
  const [page, setPage] = useState(1)
  const [data, setData] = useState<TradesData>(trades)

  async function goToPage(p: number) {
    const result = await getTrades(p)
    setData(result)
    setPage(p)
  }

  const cols = ['Time', 'Pair', 'Regime', 'Strategy', 'Action', 'Score', 'Entry', 'Outcome']

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{
          fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--text-3)', textTransform: 'uppercase',
        }}>
          Trade History ({data.total} total)
        </span>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button onClick={() => goToPage(page - 1)} disabled={page <= 1} style={pageBtnStyle(page <= 1)}>
            ←
          </button>
          <span style={{ fontSize: 12, color: 'var(--text-2)', fontFamily: 'var(--font-mono)' }}>
            {page} / {data.pages}
          </span>
          <button onClick={() => goToPage(page + 1)} disabled={page >= data.pages} style={pageBtnStyle(page >= data.pages)}>
            →
          </button>
        </div>
      </div>
      {data.items.length === 0 ? (
        <div style={{ padding: '32px', fontSize: 12, color: 'var(--text-3)', textAlign: 'center' }}>
          No trades yet
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr>
              {cols.map(h => (
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
            {data.items.map(t => (
              <tr key={t.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-2)', fontSize: 11 }}>
                  {new Date(t.timestamp).toLocaleString('en-US', {
                    month: 'short', day: 'numeric',
                    hour: '2-digit', minute: '2-digit', hour12: false,
                  })}
                </td>
                <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                  {t.pair}
                </td>
                <td style={{ padding: '9px 16px', color: 'var(--text-2)', textTransform: 'uppercase', fontSize: 11 }}>
                  {t.regime}
                </td>
                <td style={{ padding: '9px 16px', color: 'var(--text-2)', fontSize: 11 }}>
                  {t.strategy === 'trend_following' ? 'TREND'
                    : t.strategy === 'mean_reversion' ? 'REVERT'
                    : t.strategy?.toUpperCase() ?? '—'}
                </td>
                <td style={{
                  padding: '9px 16px',
                  color: t.action === 'long' ? 'var(--green)'
                    : t.action === 'short' ? 'var(--red)'
                    : 'var(--text-2)',
                  fontWeight: 700, textTransform: 'uppercase', fontSize: 11,
                }}>
                  {t.action}
                </td>
                <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)' }}>
                  {t.signal_score.toFixed(2)}
                </td>
                <td style={{ padding: '9px 16px', fontFamily: 'var(--font-mono)' }}>
                  {t.entry_price?.toFixed(2) ?? '—'}
                </td>
                <td style={{
                  padding: '9px 16px',
                  fontWeight: 700, textTransform: 'uppercase', fontSize: 11,
                  color: t.outcome === 'win' ? 'var(--green)'
                    : t.outcome === 'loss' ? 'var(--red)'
                    : 'var(--text-3)',
                }}>
                  {t.outcome ?? 'OPEN'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
