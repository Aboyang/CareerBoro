import { useRef, useState } from "react"
import ChatMessage from "./ChatMessage"
import ChatInput from "./ChatInput"
import './Chat.css'

// Only the fetch question gets settings injected
const recommendedQuestions = [
  { label: "Fetch for me 2 roles based on my profile.", injectSettings: true },
  { label: "Research about the common interview questions for AI engineer.", injectSettings: false },
  { label: "What is the difference between ML and AI engineer, and what to learn?", injectSettings: false },
  { label: "Based on my resume, what could be improved for the selected role. (Select a role)", injectSettings: false },
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
  }
}

// ── Build a context preamble from settings ────────────────────────────────────
function buildSettingsContext(settings) {
  const { expLevels, roles, locations } = settings
  const lines = []

  if (expLevels.length) lines.push(`Experience level(s): ${expLevels.join(", ")}`)
  if (roles.length)     lines.push(`Target role(s): ${roles.join(", ")}`)
  if (locations.length) lines.push(`Preferred location(s): ${locations.join(", ")}`)

  if (!lines.length) return null

  return `[User job search preferences]\n${lines.join("\n")}\n\nFor each role or company mentioned, also research the company's current initiatives relevant to the role's department.`
}

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
    text = text.trim()
    if (!text) return

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


  // Clicking populates the input with the FULL prompt (injected if applicable)
  // so the user can read, tweak, and send
  const handleRecommendedClick = (question) => {
    const prompt = question.injectSettings
      ? buildPromptWithContext(question.label)
      : question.label
    setInputValue(prompt)
  }

  // On send, just fire whatever is in the input — no further transformation
  const handleInputSend = () => {
    const trimmed = inputValue.trim()
    if (!trimmed) return
    handleSend(trimmed)
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
                {q.label}
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
        onSend={handleInputSend}
        disabled={streaming}
      />
    </div>
  )
}