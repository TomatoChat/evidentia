"use client"

import { useState } from 'react'
import { Button } from '../components/Header'

export default function HomePage() {
  const [email, setEmail] = useState('')
  const [showBrandForm, setShowBrandForm] = useState(false)
  const [brandData, setBrandData] = useState({
    brandName: '',
    brandWebsite: '',
    brandCountry: ''
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return
    
    // You can send email to backend here if needed
    console.log('Email collected:', email)
    setShowBrandForm(true)
  }

  const handleBrandSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // Replace with your actual backend URL
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/stream-brand-info`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          brandName: brandData.brandName,
          brandWebsite: brandData.brandWebsite,
          brandCountry: brandData.brandCountry || 'world'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to analyze brand')
      }

      // Handle streaming response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ') && line.trim().length > 6) {
              try {
                const jsonData = line.slice(6).trim()
                if (jsonData) {
                  const data = JSON.parse(jsonData)
                  
                  if (data.error) {
                    throw new Error(data.error)
                  }
                  
                  if (data.step === 'complete' && data.result) {
                    setResults(data.result)
                  }
                }
              } catch (parseError) {
                console.warn('Failed to parse JSON:', line, parseError)
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error analyzing brand:', error)
      alert('Error analyzing brand: ' + (error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (showBrandForm) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 max-w-2xl w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">Brand Analysis</h1>
            <p className="text-gray-600 text-lg">Tell us about your brand for comprehensive research</p>
          </div>

          <form onSubmit={handleBrandSubmit} className="space-y-6">
            <div>
              <label htmlFor="brandName" className="block text-sm font-semibold text-gray-700 mb-2">
                Brand Name
              </label>
              <input
                type="text"
                id="brandName"
                value={brandData.brandName}
                onChange={(e) => setBrandData({...brandData, brandName: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-gray-800 focus:border-purple-500 focus:outline-none transition-colors"
                placeholder="e.g., jethr"
                required
              />
            </div>

            <div>
              <label htmlFor="brandWebsite" className="block text-sm font-semibold text-gray-700 mb-2">
                Brand Website
              </label>
              <input
                type="text"
                id="brandWebsite"
                value={brandData.brandWebsite}
                onChange={(e) => setBrandData({...brandData, brandWebsite: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-gray-800 focus:border-purple-500 focus:outline-none transition-colors"
                placeholder="e.g., jethr.com"
                required
              />
            </div>

            <div>
              <label htmlFor="brandCountry" className="block text-sm font-semibold text-gray-700 mb-2">
                Brand Country (Optional)
              </label>
              <input
                type="text"
                id="brandCountry"
                value={brandData.brandCountry}
                onChange={(e) => setBrandData({...brandData, brandCountry: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-gray-800 focus:border-purple-500 focus:outline-none transition-colors"
                placeholder="e.g., italy (defaults to 'world')"
              />
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '🔄 Analyzing...' : '🚀 Analyze Brand'}
              </button>
            </div>
          </form>

          {results && (
            <div className="mt-8 p-6 bg-gray-50 rounded-xl">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📊 Brand Information</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>Name:</strong> {(results as any).name}</p>
                <p><strong>Description:</strong> {(results as any).description}</p>
                <p><strong>Industry:</strong> {(results as any).industry}</p>
                <p><strong>Competitors:</strong></p>
                <pre className="bg-white p-3 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify((results as any).competitors, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">🔍 Welcome</h1>
          <p className="text-gray-600 text-lg leading-relaxed">
            Get started with comprehensive brand research and competitive analysis
          </p>
        </div>

        <form onSubmit={handleEmailSubmit} className="space-y-6">
          <div className="text-left">
            <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-gray-800 focus:border-purple-500 focus:outline-none transition-colors"
              placeholder="Enter your email address"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 transform hover:scale-105"
          >
            Get Started
          </button>
        </form>
      </div>
    </div>
  )
}