'use client'
import { useEffect, useRef, useState } from 'react'
import type { WsEvent } from './types'

export function useWebSocket(): WsEvent | null {
  const [event, setEvent] = useState<WsEvent | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const wsUrl = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000')
      .replace(/^http/, 'ws') + '/stream'

    function connect() {
      ws.current = new WebSocket(wsUrl)
      ws.current.onmessage = (e) => {
        try { setEvent(JSON.parse(e.data) as WsEvent) } catch {}
      }
      ws.current.onclose = () => {
        timer.current = setTimeout(connect, 3000)
      }
    }

    connect()
    return () => {
      if (timer.current) clearTimeout(timer.current)
      ws.current?.close()
    }
  }, [])

  return event
}
