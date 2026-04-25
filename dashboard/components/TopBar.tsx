'use client'
import { useEffect, useState } from 'react'
import type { StatusData } from '@/lib/types'

export function TopBar({ status }: { status: StatusData }) {
  const [time, setTime] = useState('')

  useEffect(() => {
    const update = () => {
      setTime(new Date().toUTCString().split(' ')[4] + ' UTC')
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  const regime = status.regime?.toUpperCase() ?? null
  const regimeColor = status.regime === 'trending'
    ? 'var(--accent)'
    : status.regime === 'ranging'
    ? 'var(--cyan)'
    : 'var(--text-3)'

  return (
    <header style={{
      height: 52,
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      gap: 20,
      flexShrink: 0,
    }}>
      {['BTC/USD', 'ETH/USD'].map(pair => (
        <span key={pair} style={{
          fontSize: 12,
          fontWeight: 600,
          color: 'var(--text-2)',
          fontFamily: 'var(--font-mono)',
          padding: '3px 8px',
          border: '1px solid var(--border)',
          borderRadius: 4,
        }}>
          {pair}
        </span>
      ))}

      {regime && (
        <div style={{
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: '0.1em',
          color: regimeColor,
          border: `1px solid ${regimeColor}`,
          borderRadius: 4,
          padding: '3px 10px',
        }}>
          {regime}
        </div>
      )}

      <div style={{ flex: 1 }} />

      <span style={{ fontSize: 12, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>
        {time}
      </span>
    </header>
  )
}
