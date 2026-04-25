'use client'
import type { Position } from '@/lib/types'

function PositionsTable({
  title,
  positions,
  showOutcome,
}: {
  title: string
  positions: Position[]
  showOutcome: boolean
}) {
  const cols = showOutcome
    ? ['Pair', 'Direction', 'Entry', 'Size', 'Opened', 'Outcome']
    : ['Pair', 'Direction', 'Entry', 'Size', 'Stop Loss', 'Take Profit']

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
        fontSize: 10, fontWeight: 700, letterSpacing: '0.1em',
        color: 'var(--text-3)', textTransform: 'uppercase',
      }}>
        {title}
      </div>
      {positions.length === 0 ? (
        <div style={{ padding: '24px', fontSize: 12, color: 'var(--text-3)', textAlign: 'center' }}>
          No positions
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
            {positions.map(p => (
              <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                  {p.pair}
                </td>
                <td style={{
                  padding: '10px 16px',
                  color: p.direction === 'long' ? 'var(--green)' : 'var(--red)',
                  fontWeight: 700, textTransform: 'uppercase', fontSize: 11,
                }}>
                  {p.direction}
                </td>
                <td style={{ padding: '10px 16px', fontFamily: 'var(--font-mono)' }}>
                  {p.entry_price.toFixed(2)}
                </td>
                <td style={{ padding: '10px 16px', fontFamily: 'var(--font-mono)' }}>
                  {p.position_size.toFixed(4)}
                </td>
                {showOutcome ? (
                  <>
                    <td style={{ padding: '10px 16px', color: 'var(--text-2)', fontSize: 11 }}>
                      {new Date(p.opened_at).toLocaleString('en-US', {
                        month: 'short', day: 'numeric',
                        hour: '2-digit', minute: '2-digit', hour12: false,
                      })}
                    </td>
                    <td style={{
                      padding: '10px 16px',
                      fontWeight: 700, textTransform: 'uppercase', fontSize: 11,
                      color: p.outcome === 'win'
                        ? 'var(--green)'
                        : p.outcome === 'loss'
                        ? 'var(--red)'
                        : 'var(--text-3)',
                    }}>
                      {p.outcome ?? '—'}
                    </td>
                  </>
                ) : (
                  <>
                    <td style={{ padding: '10px 16px', fontFamily: 'var(--font-mono)', color: 'var(--red)' }}>
                      {p.stop_loss?.toFixed(2) ?? '—'}
                    </td>
                    <td style={{ padding: '10px 16px', fontFamily: 'var(--font-mono)', color: 'var(--green)' }}>
                      {p.take_profit?.toFixed(2) ?? '—'}
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export function Positions({ positions }: { positions: Position[] }) {
  const open   = positions.filter(p => p.is_open === 1)
  const closed = positions.filter(p => p.is_open === 0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <PositionsTable
        title={`Open Positions (${open.length})`}
        positions={open}
        showOutcome={false}
      />
      <PositionsTable
        title={`Closed Positions (${closed.length})`}
        positions={closed}
        showOutcome={true}
      />
    </div>
  )
}
