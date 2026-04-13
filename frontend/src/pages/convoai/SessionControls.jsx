import { useState } from "react";
import { CloudLightning, CloudOff, MessageSquare } from "react-feather";
import Button from "./Button";
import "./SessionControls.css";

function SessionStopped({ startSession }) {
  const [isActivating, setIsActivating] = useState(false);

  function handleStartSession() {
    if (isActivating) return;
    setIsActivating(true);
    startSession();
  }

  return (
    <div className="session-controls">
      <Button
        onClick={handleStartSession}
        className={`session-btn--start ${isActivating ? "activating" : ""}`}
        icon={<CloudLightning height={15} />}
      >
        {isActivating ? "Starting session…" : "Launch session"}
      </Button>
    </div>
  );
}

function SessionActive({ stopSession, sendTextMessage }) {
  const [message, setMessage] = useState("");

  function handleSend() {
    if (!message.trim()) return;
    sendTextMessage(message);
    setMessage("");
  }

  return (
    <div className="session-controls">
      <input
        type="text"
        placeholder="Type a message…"
        className="session-controls__input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <Button
        onClick={handleSend}
        className="session-btn--send"
        icon={<MessageSquare height={14} />}
      >
        Send
      </Button>
      <Button
        onClick={stopSession}
        className="session-btn--stop"
        icon={<CloudOff height={14} />}
      >
        End
      </Button>
    </div>
  );
}

export default function SessionControls({
  startSession,
  stopSession,
  sendClientEvent,
  sendTextMessage,
  serverEvents,
  isSessionActive,
}) {
  return isSessionActive ? (
    <SessionActive
      stopSession={stopSession}
      sendClientEvent={sendClientEvent}
      sendTextMessage={sendTextMessage}
      serverEvents={serverEvents}
    />
  ) : (
    <SessionStopped startSession={startSession} />
  );
}