import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'DataSync Pro - Enterprise Data Solutions',
  description: 'Transform your business with AI-powered analytics and real-time data processing solutions.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}: any) {
  return (
    <html lang='en'>
      <body className={inter.className}>{children}</body>
    </html>
  )
}