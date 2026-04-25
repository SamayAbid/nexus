'use client'
import { useState, useRef } from 'react'
import type { CSSProperties } from 'react'
import type { StatusData } from '@/lib/types'
import { postControl } from '@/lib/api'

interface LogEntry {
  id: number
  time: string
  message: string
  ok: boolean
}

function ctrlBtnStyle(color: string, disabled: boolean): CSSProperties {
  return {
    padding: '10px 20px',
    background: `${color}18`,
    border: `1px solid ${color}`,
    borderRadius: 6,
    color,
    fontSize: 13,
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'all 0.15s',
    fontFamily: 'var(--font-sans)',
    letterSpacing: '0.04em',
  }
}

export function Control({ status, onChanged }: { status: StatusData; onChanged: () => void }) {
  const [confirming, setConfirming] = useState(false)
  const [loading, setLoading]       = useState(false)
  const [log, setLog]               = useState<LogEntry[]>([])
  const confirmTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const logId = useRef(0)

  function addLog(message: string, ok: boolean) {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false })
    const id = ++logId.current
    setLog(prev => [{ id, time, message, ok }, ...prev].slice(0, 20))
  }

  async function handlePause() {
    if (!confirming) {
      confirmTimer.current = setTimeout(() => setConfirming(false), 3000)
      setConfirming(true)
      return
    }
    clearTimeout(confirmTimer.current ?? undefined)
    confirmTimer.current = null
    setConfirming(false)
    setLoading(true)
    try {
      await postControl('pause')
      addLog('Agent paused', true)
      onChanged()
    } catch {
      addLog('Pause failed — API error', false)
    } finally {
      setLoading(false)
    }
  }

  async function handleResume() {
    setLoading(true)
    try {
      await postControl('resume')
      addLog('Agent resumed', true)
      onChanged()
    } catch {
      addLog('Resume failed — API error', false)
    } finally {
      setLoading(false)
    }
  }

  const stateColor = status.is_paused
    ? 'var(--yellow)'
    : status.is_running
    ? 'var(--green)'
    : 'var(--text-3)'
  const stateLabel = status.is_paused ? 'PAUSED' : status.is_running ? 'RUNNING' : 'OFFLINE'
  const stateIcon  = status.is_paused ? '⏸' : status.is_running ? '▶' : '○'

  const uptime = `${Math.floor(status.uptime_seconds / 3600)}h ${Math.floor((status.uptime_seconds % 3600) / 60)}m`

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Agent status hero */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: 20,
      }}>
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          background: `${stateColor}18`,
          border: `2px solid ${stateColor}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 26,
          boxShadow: status.is_running && !status.is_paused ? `0 0 24px ${stateColor}40` : 'none',
          flexShrink: 0,
        }}>
          {stateIcon}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 20, fontWeight: 700, color: stateColor,
            letterSpacing: '0.08em', textTransform: 'uppercase',
          }}>
            {stateLabel}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-2)', marginTop: 6, fontFamily: 'var(--font-mono)' }}>
            Uptime: {uptime} · Pair: {status.pair ?? '—'} · Strategy: {status.strategy?.toUpperCase() ?? '—'}
          </div>
        </div>
        <div>
          {status.is_paused ? (
            <button onClick={handleResume} disabled={loading} style={ctrlBtnStyle('var(--green)', loading)}>
              {loading ? '…' : '▶  Resume Agent'}
            </button>
          ) : (
            <button
              onClick={handlePause}
              disabled={loading}
              style={ctrlBtnStyle(confirming ? 'var(--red)' : 'var(--yellow)', loading)}
            >
              {loading ? '…' : confirming ? '⚠  Confirm Pause?' : '⏸  Pause Agent'}
            </button>
          )}
        </div>
      </div>

      {/* System info */}
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
          System Info
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          {[
            { label: 'Active Pair',    value: status.pair ?? '—' },
            { label: 'Regime',         value: status.regime?.toUpperCase() ?? '—' },
            {
              label: 'Last Heartbeat',
              value: status.last_heartbeat
                ? new Date(status.last_heartbeat).toLocaleTimeString('en-US', { hour12: false })
                : '—',
            },
          ].map(item => (
            <div key={item.label} style={{
              padding: 12,
              background: 'var(--bg)',
              borderRadius: 6,
              border: '1px solid var(--border)',
            }}>
              <div style={{
                fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
                color: 'var(--text-3)', textTransform: 'uppercase', marginBottom: 8,
              }}>
                {item.label}
              </div>
              <div style={{
                fontSize: 15, fontFamily: 'var(--font-mono)',
                color: 'var(--text-1)', fontWeight: 600,
              }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Event log */}
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
          Event Log
        </div>
        {log.length === 0 ? (
          <div style={{ padding: '24px', fontSize: 12, color: 'var(--text-3)', textAlign: 'center' }}>
            No events — use the controls above to pause or resume the agent
          </div>
        ) : (
          <div style={{ maxHeight: 220, overflowY: 'auto' }}>
            {log.map(entry => (
              <div key={entry.id} style={{
                padding: '8px 16px',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                gap: 14,
                fontSize: 12,
              }}>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-3)', flexShrink: 0 }}>
                  {entry.time}
                </span>
                <span style={{ color: entry.ok ? 'var(--green)' : 'var(--red)' }}>
                  {entry.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
