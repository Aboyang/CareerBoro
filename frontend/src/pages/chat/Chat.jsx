import { useRef, useState } from "react"
import ChatMessage from "./ChatMessage"
import ChatInput from "./ChatInput"
import './Chat.css'

const recommendedQuestions = [
  { label: "Fetch for me 2 roles based on my profile.", injectSettings: true },

  { label: "Research about the common interview questions for AI engineer.", injectSettings: false },

  { label: "Send an email to [name] at [email address].", injectSettings: false },

  {
    label: "Based on my resume, compute my match score for the selected role, and tell me what I may miss. [Select a role",
    injectSettings: "job"
  },
]

/* -----------------------------
   Local storage loader
------------------------------*/
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
    roles: read("settings:roles", []),
    locations: read("settings:locations", []),

    // NEW
    profile: read("settings:profile", null),
    selectedJob: read("selectedJob", null),
  }
}

/* -----------------------------
   Context builders
------------------------------*/
function buildSettingsContext(settings) {
  const { expLevels, roles, locations } = settings

  const lines = []
  if (expLevels.length) lines.push(`Experience level(s): ${expLevels.join(", ")}`)
  if (roles.length) lines.push(`Target role(s): ${roles.join(", ")}`)
  if (locations.length) lines.push(`Preferred location(s): ${locations.join(", ")}`)

  if (!lines.length) return null

  return `[User job search preferences]\n${lines.join("\n")}`
}

function buildJobAnalysisContext(settings) {
  const { profile, selectedJob } = settings

  const lines = []

  if (profile) {
    lines.push(`User Profile:\n${JSON.stringify(profile, null, 2)}`)
  }

  if (selectedJob?.job_desc) {
    lines.push(`Selected Job Description:\n${selectedJob.job_desc}`)
  }

  if (!lines.length) return null

  return `[Resume + Job Analysis Context]\n${lines.join("\n\n")}`
}

/* -----------------------------
   Prompt builder
------------------------------*/
function buildPromptWithContext(question, includeJobContext = false) {
  const settings = loadSettings()

  const searchContext = buildSettingsContext(settings)
  const jobContext = includeJobContext
    ? buildJobAnalysisContext(settings)
    : null

  const contextParts = [searchContext, jobContext].filter(Boolean)

  if (!contextParts.length) return question

  return `${contextParts.join("\n\n")}\n\n${question}`
}

/* -----------------------------
   Streaming
------------------------------*/
const SENTINEL = "---FINAL---"

async function streamChat(prompt, onChunk, onDone) {
  const res = await fetch("http://localhost:8000/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  })

  const reader = res.body.getReader()
  const decoder = new TextDecoder()

  let buffer = ""

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    if (buffer.includes(SENTINEL)) {
      const [status, final] = buffer.split(SENTINEL)

      onChunk({
        status: status.trim(),
        final: final ?? ""
      })
    } else {
      onChunk({
        status: buffer.trim(),
        final: ""
      })
    }
  }

  onDone?.()
}

/* -----------------------------
   Component
------------------------------*/
export default function Chat() {
  const [messages, setMessages] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [inputValue, setInputValue] = useState("")

  const assistantIndexRef = useRef(null)

  async function handleSend(text) {
    text = text.trim()
    if (!text) return

    const userMsg = { role: "user", content: text }
    const assistantMsg = { role: "assistant", content: "", status: "" }

    setMessages(prev => {
      const newMsgs = [...prev, userMsg, assistantMsg]
      assistantIndexRef.current = newMsgs.length - 1
      return newMsgs
    })

    setInputValue("")
    setStreaming(true)

    await streamChat(
      text,
      ({ status, final }) => {
        setMessages(prev => {
          const copy = [...prev]

          copy[assistantIndexRef.current] = {
            role: "assistant",
            status,
            content: final
          }

          return copy
        })
      },
      () => setStreaming(false)
    )
  }

  /* -----------------------------
     Recommended click logic
  ------------------------------*/
  const handleRecommendedClick = (question) => {
    let prompt

    if (question.injectSettings === true) {
      prompt = buildPromptWithContext(question.label, false)
    }

    else if (question.injectSettings === "job") {
      prompt = buildPromptWithContext(question.label, true)
    }

    else {
      prompt = question.label
    }

    setInputValue(prompt)
  }

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
            status={m.status}
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