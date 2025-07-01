import './globals.css'

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
        <main>
          {children}
        </main>
      </body>
    </html> 
  )
}