import './Chat.css'

export default function ChatInput({ value, onChange, onSend, disabled }) {

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (value.trim()) {
        onSend()
      }
    }
  }

  return (
    <div className="chat-input-container">
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)} // editable typing works
        onKeyDown={handleKeyDown}
        placeholder="Ask about patients…"
        disabled={disabled}
        className="chat-input"
      />
      <button
        onClick={() => {
          if (value.trim()) {
            onSend()
          }
        }}
        disabled={disabled}
        className="chat-input-button"
      >
        Send
      </button>
    </div>
  )
}
