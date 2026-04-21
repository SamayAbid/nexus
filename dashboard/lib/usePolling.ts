'use client'
import { useEffect, useState, useCallback } from 'react'

export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number,
  initial: T,
): T {
  const [data, setData] = useState<T>(initial)

  const run = useCallback(async () => {
    try { setData(await fetcher()) } catch {}
  }, [fetcher])

  useEffect(() => {
    run()
    const id = setInterval(run, intervalMs)
    return () => clearInterval(id)
  }, [run, intervalMs])

  return data
}
