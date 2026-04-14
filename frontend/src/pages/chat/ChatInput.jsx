import { useRef, useEffect } from "react";
import './Chat.css';

export default function ChatInput({ value, onChange, onSend, disabled }) {
  const textareaRef = useRef(null);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) {
        onSend();
      }
    }
  }

  function resizeTextarea() {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "auto";             
    el.style.height = el.scrollHeight + "px"; 
  }

  function handleChange(e) {
    onChange(e.target.value);
  }

  useEffect(() => {
    resizeTextarea();
  }, [value]);

  return (
    <div className="chat-input-container">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Find me an internship…"
        disabled={disabled}
        className="chat-input"
      />
      <button
        onClick={() => {
          if (value.trim()) {
            onSend();
          }
        }}
        disabled={disabled}
        className="chat-input-button"
      >
        Send
      </button>
    </div>
  );
}