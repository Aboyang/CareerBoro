import { useRef, useState } from "react"
import ChatMessage from "./ChatMessage"
import ChatInput from "./ChatInput"
import './Chat.css'

const recommendedQuestions = [
  "Fetch for me 2 roles based on my profile.",
  "For each of my job listings, research the company's current initiatives relevant to the role's department.",
  "Research about the common interview questions for AI engineer.",
  "What is the different between ML and AI engineer?",
  "Based on my resume, what could be improved for the selected role. (Select a role)"
]

// ── Read job search settings from localStorage ────────────────────────────────
function loadSettings() {
  const read = (key, fallback) => {
    try {
      const raw = localStorage.getItem(key)
      return raw !== null ? JSON.parse(raw) : fallback
    } catch {
      return fallback
    }
  }

  return {
    expLevels: read("settings:expLevels", []),
    roles:     read("settings:roles", []),
    locations: read("settings:locations", []),
    fetchTime: read("settings:fetchTime", null),
  }
}

// ── Build a context preamble from settings ────────────────────────────────────
function buildSettingsContext(settings) {
  const { expLevels, roles, locations } = settings
  const lines = []

  if (expLevels.length)  lines.push(`Experience level(s): ${expLevels.join(", ")}`)
  if (roles.length)      lines.push(`Target role(s): ${roles.join(", ")}`)
  if (locations.length)  lines.push(`Preferred location(s): ${locations.join(", ")}`)

  if (!lines.length) return null

  return `[User job search preferences]\n${lines.join("\n")}\n\nFor each role or company mentioned, also research the company's current initiatives relevant to the role's department.`
}

// ── Inject settings context only for recommended questions ────────────────────
function buildPromptWithContext(question) {
  const settings = loadSettings()
  const context = buildSettingsContext(settings)
  if (!context) return question
  return `${context}\n\n${question}`
}

async function streamChat(prompt, onChunk, onDone) {
  const res = await fetch("http://localhost:8000/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  })

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let text = ""

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    text += decoder.decode(value, { stream: true })
    onChunk(text)
  }

  onDone?.()
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [inputValue, setInputValue] = useState("")
  const assistantIndexRef = useRef(null)

  async function handleSend(text) {
    if (!text.trim()) return

    const userMsg = { role: "user", content: text }
    const assistantMsg = { role: "assistant", content: "" }

    setMessages(prev => {
      const newMsgs = [...prev, userMsg, assistantMsg]
      assistantIndexRef.current = newMsgs.length - 1
      return newMsgs
    })

    setInputValue("")
    setStreaming(true)

    await streamChat(
      text,
      chunk => {
        setMessages(prev => {
          const copy = [...prev]
          copy[assistantIndexRef.current] = { role: "assistant", content: chunk }
          return copy
        })
      },
      () => setStreaming(false)
    )
  }

  // Recommended questions: display text shown to user, enriched prompt sent to backend
  const handleRecommendedClick = (question) => {
    const enrichedPrompt = buildPromptWithContext(question)

    // Show the original question text in the chat UI (not the raw preamble)
    const userMsg = { role: "user", content: question }
    const assistantMsg = { role: "assistant", content: "" }

    setMessages(prev => {
      const newMsgs = [...prev, userMsg, assistantMsg]
      assistantIndexRef.current = newMsgs.length - 1
      return newMsgs
    })

    setStreaming(true)

    streamChat(
      enrichedPrompt,   // ← enriched version goes to the backend
      chunk => {
        setMessages(prev => {
          const copy = [...prev]
          copy[assistantIndexRef.current] = { role: "assistant", content: chunk }
          return copy
        })
      },
      () => setStreaming(false)
    )
  }

  return (
    <div className="chat-wrapper">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="recommended-grid">
            {recommendedQuestions.map((q, i) => (
              <button
                key={i}
                className="recommended-btn"
                onClick={() => handleRecommendedClick(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <ChatMessage
            key={i}
            role={m.role}
            content={m.content}
            streaming={streaming && i === assistantIndexRef.current}
          />
        ))}
      </div>

      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSend={() => handleSend(inputValue)}
        disabled={streaming}
      />
    </div>
  )
}