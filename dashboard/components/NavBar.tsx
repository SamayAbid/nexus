'use client'
import { useState } from 'react'
import type { StatusData } from '@/lib/types'
import { postControl } from '@/lib/api'

interface NavBarProps {
  status: StatusData
  onControlChange: () => void
}

export function NavBar({ status, onControlChange }: NavBarProps) {
  const [confirming, setConfirming] = useState(false)

  async function handleControl() {
    if (status.is_paused) {
      await postControl('resume')
      onControlChange()
    } else if (confirming) {
      await postControl('pause')
      setConfirming(false)
      onControlChange()
    } else {
      setConfirming(true)
      setTimeout(() => setConfirming(false), 3000)
    }
  }

  return (
    <nav className="nav-bar">
      <div className="nav-left">
        <span className="nav-logo">NEXUS</span>
        <div className={`live-indicator ${status.is_running ? 'live' : 'offline'}`}>
          <span className="live-dot" />
          <span>{status.is_running ? 'LIVE' : 'OFFLINE'}</span>
        </div>
      </div>

      <div className="nav-center">
        <span className="nav-pair">BTC/USD</span>
        <span className="nav-pair">ETH/USD</span>
        {status.regime && (
          <span className={`regime-badge ${status.regime}`}>
            REGIME: {status.regime.toUpperCase()}
          </span>
        )}
      </div>

      <div className="nav-right">
        <button
          className={`control-btn${status.is_paused ? ' paused' : confirming ? ' confirming' : ''}`}
          onClick={handleControl}
        >
          {status.is_paused ? '▶ RESUME' : confirming ? 'CONFIRM PAUSE?' : '⏸ PAUSE'}
        </button>
      </div>
    </nav>
  )
}
