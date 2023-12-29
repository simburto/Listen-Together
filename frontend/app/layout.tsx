import { authOptions } from '@/pages/api/auth/[...nextauth]'
import type { Metadata } from 'next'
import { getServerSession } from 'next-auth'
import { Inter } from 'next/font/google'
import './globals.css'
import AuthProvider from './SessionProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Listen Together',
  description: 'Listen together across multiple streaming platforms!',
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession(authOptions);
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider session={session}>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
