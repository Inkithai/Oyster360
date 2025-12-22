'use client'

import { useState } from 'react'
import { apiRequest } from '@/lib/api'

export default function AIAssistantPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const askQuestion = async () => {
    if (!question.trim()) return
    
    setLoading(true)
    try {
      const res = await apiRequest('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ question }),
      })
      setAnswer(res.answer)
    } catch {
      setAnswer("Sorry, the AI assistant is currently unavailable.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-2">MycelForge AI Assistant</h1>
      <p className="text-muted-foreground mb-8">Ask questions about your oyster mushroom cultivation</p>

      <div className="space-y-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Why is Batch OY-2026-002 growing slowly?"
            className="flex-1 border rounded-lg px-4 py-3"
            onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
          />
          <button 
            onClick={askQuestion}
            disabled={loading}
            className="px-6 py-3 bg-black text-white rounded-lg disabled:opacity-50"
          >
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </div>

        {answer && (
          <div className="border rounded-xl p-6 bg-muted/30">
            <div className="font-medium text-sm text-muted-foreground mb-2">AI Response</div>
            <p className="text-lg">{answer}</p>
          </div>
        )}
      </div>
    </div>
  )
}