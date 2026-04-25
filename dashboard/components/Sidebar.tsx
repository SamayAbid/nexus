'use client'

export type Tab = 'overview' | 'signals' | 'positions' | 'trades' | 'risk' | 'control'

const NAV_ITEMS: { id: Tab; label: string; icon: string }[] = [
  { id: 'overview',  label: 'Overview',  icon: '◈' },
  { id: 'signals',   label: 'Signals',   icon: '◎' },
  { id: 'positions', label: 'Positions', icon: '▣' },
  { id: 'trades',    label: 'Trades',    icon: '≡' },
  { id: 'risk',      label: 'Risk',      icon: '⚠' },
  { id: 'control',   label: 'Control',   icon: '⏻' },
]

interface SidebarProps {
  active: Tab
  onChange: (tab: Tab) => void
  isRunning: boolean
  isPaused: boolean
}

export function Sidebar({ active, onChange, isRunning, isPaused }: SidebarProps) {
  const statusColor = isPaused ? 'var(--yellow)' : isRunning ? 'var(--green)' : 'var(--text-3)'
  const statusLabel = isPaused ? 'PAUSED' : isRunning ? 'LIVE' : 'OFFLINE'

  return (
    <aside style={{
      width: 220,
      background: 'var(--surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="6" fill="var(--accent)" fillOpacity="0.15" />
            <path d="M8 20L14 8L20 20M10.5 15H17.5" stroke="var(--accent)" strokeWidth="1.8"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span style={{
            fontSize: 18, fontWeight: 700, letterSpacing: '0.1em', color: 'var(--text-1)',
          }}>
            NEXUS
          </span>
        </div>
      </div>

      <nav style={{ flex: 1, padding: '12px 8px' }}>
        {NAV_ITEMS.map(item => {
          const isActive = active === item.id
          return (
            <button
              key={item.id}
              onClick={() => onChange(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 12px',
                marginBottom: 2,
                borderRadius: 6,
                border: 'none',
                borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                background: isActive ? 'var(--accent-dim)' : 'transparent',
                color: isActive ? 'var(--accent)' : 'var(--text-2)',
                fontSize: 14,
                fontWeight: isActive ? 600 : 400,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s',
              }}
            >
              <span style={{ fontSize: 16 }}>{item.icon}</span>
              {item.label}
            </button>
          )
        })}
      </nav>

      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: statusColor,
            boxShadow: isRunning && !isPaused ? `0 0 8px ${statusColor}` : 'none',
          }} />
          <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: statusColor }}>
            {statusLabel}
          </span>
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
          NEXUS Agent v2.0
        </div>
      </div>
    </aside>
  )
}
