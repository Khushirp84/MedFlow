import { useState, useEffect, useRef } from 'react'
import type { ChatMessage } from '../types'
import { askQuestion, getChatHistory } from '../api/endpoints'

export default function ChatBox({ patientId }: { patientId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [question, setQuestion] = useState('')
  const [asking, setAsking] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getChatHistory(patientId).then(setMessages).catch(() => {})
  }, [patientId])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [messages])

  async function handleAsk() {
    if (!question.trim() || asking) return
    const q = question
    setQuestion('')
    setAsking(true)
    setMessages((prev) => [
      ...prev,
      { id: `temp-${Date.now()}`, role: 'user', content: q, created_at: new Date().toISOString() },
    ])
    try {
      const result = await askQuestion(patientId, q)
      setMessages((prev) => [
        ...prev,
        {
          id: `temp-a-${Date.now()}`,
          role: 'assistant',
          content: result.answer,
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-slate-200 bg-white">
      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <p className="text-sm text-slate-300">
            Ask about this patient's uploaded documents, e.g. "What medications were prescribed?"
          </p>
        )}
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span
              className={`inline-block max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                m.role === 'user' ? 'bg-teal-500 text-white' : 'bg-slate-100 text-ink'
              }`}
            >
              {m.content}
            </span>
          </div>
        ))}
        {asking && <p className="text-sm text-slate-300">Thinking…</p>}
      </div>
      <div className="flex gap-2 border-t border-slate-200 p-3">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a question about this patient…"
          className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-400"
        />
        <button
          onClick={handleAsk}
          disabled={asking}
          className="rounded-md bg-teal-500 px-4 py-2 text-sm font-medium text-white hover:bg-teal-600 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  )
}
