'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'

export default function AIAssistantPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [batchId, setBatchId] = useState<number | undefined>()

  const chatMutation = useMutation({
    mutationFn: (q: string) =>
      apiRequest('/api/assistant/chat', {
        method: 'POST',
        body: JSON.stringify({ question: q, batch_id: batchId }),
      }),
    onSuccess: (data) => {
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    },
  })

  const sendMessage = () => {
    if (!question.trim()) return

    setMessages(prev => [...prev, { role: 'user', content: question }])
    chatMutation.mutate(question)
    setQuestion('')
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Oyster360 AI Farm Copilot</h1>
        <p className="text-muted-foreground">Your intelligent assistant for oyster mushroom cultivation</p>
      </div>

      {/* Suggested Questions */}
      <div className="mb-6">
        <div className="text-sm font-medium mb-2">Suggested Questions</div>
        <div className="flex flex-wrap gap-2">
          {[
            "Why is Batch B-104 growing slowly?",
            "What recipe has the highest yield?",
            "Show contamination trends this month",
            "Compare Batch 102 and 103"
          ].map((q, i) => (
            <button
              key={i}
              onClick={() => {
                setQuestion(q)
                setMessages(prev => [...prev, { role: 'user', content: q }])
                chatMutation.mutate(q)
              }}
              className="text-xs px-3 py-1.5 border rounded-full hover:bg-muted"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="border rounded-xl h-[500px] flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground pt-12">
              Ask anything about your farm, batches, recipes, or cultivation practices.
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={msg.role === 'user' ? 'text-right' : ''}>
              <div className={`inline-block max-w-[85%] rounded-2xl px-5 py-3 text-sm ${
                msg.role === 'user' 
                  ? 'bg-black text-white' 
                  : 'bg-muted'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about batches, recipes, yield, or cultivation..."
              className="flex-1 border rounded-xl px-5 py-3 text-sm"
            />
            <button
              onClick={sendMessage}
              disabled={chatMutation.isPending}
              className="bg-black text-white px-8 rounded-xl text-sm font-medium disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Context Controls */}
      <div className="mt-4 flex items-center gap-4 text-sm">
        <div>
          <label className="text-muted-foreground">Focus on Batch:</label>
          <input 
            type="number" 
            value={batchId || ''} 
            onChange={e => setBatchId(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="Optional"
            className="ml-2 w-24 border rounded px-3 py-1 text-sm" 
          />
        </div>
      </div>
    </div>
  )
}