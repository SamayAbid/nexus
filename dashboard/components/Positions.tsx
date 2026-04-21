'use client'
import type { Position } from '@/lib/types'

export function Positions({ positions }: { positions: Position[] }) {
  return (
    <div className="panel positions-panel">
      <div className="panel-header">
        <span className="panel-title">OPEN POSITIONS</span>
        <span style={{ fontSize: 10, color: 'var(--text-secondary)', fontFamily: 'var(--font-condensed)' }}>
          {positions.length}/3
        </span>
      </div>

      {positions.length === 0 ? (
        <div className="empty-state">NO OPEN POSITIONS</div>
      ) : (
        <div style={{ overflow: 'auto', flex: 1 }}>
          <table className="positions-table">
            <thead>
              <tr>
                {['PAIR', 'DIR', 'ENTRY', 'SL', 'TP', 'SIZE $'].map(h => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {positions.map(p => (
                <tr key={p.id}>
                  <td>{p.pair}</td>
                  <td className={p.direction}>{p.direction.toUpperCase()}</td>
                  <td>${p.entry_price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</td>
                  <td className="negative">${p.stop_loss.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</td>
                  <td className="positive">${p.take_profit.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</td>
                  <td>${p.position_size.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
