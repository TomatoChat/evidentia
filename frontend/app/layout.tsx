import './globals.css'
import { Header } from '../components/Header'

export const metadata = {
  title: 'Evidentia - Brand Research Tool',
  description: 'Comprehensive brand research and competitive analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-600">
        <Header 
          className="fixed top-0 left-0 right-0 z-50"
          theme="dark"
          isStickyOverlay={true}
          logo={
            <div className="text-white font-bold text-xl">
              🔍 Evidentia
            </div>
          }
        />
        <main className="pt-20">
          {children}
        </main>
      </body>
    </html>
  )
}