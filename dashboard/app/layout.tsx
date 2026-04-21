import type { Metadata } from 'next'
import { IBM_Plex_Mono, Barlow_Condensed } from 'next/font/google'
import './globals.css'

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono',
})

const barlowCondensed = Barlow_Condensed({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-condensed',
})

export const metadata: Metadata = {
  title: 'NEXUS — AI Trading Agent',
  description: 'Real-time paper trading dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${ibmPlexMono.variable} ${barlowCondensed.variable}`}>
      <body>{children}</body>
    </html>
  )
}
