import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import "./ConvoAI.css"
import VoiceIndicator from "./VoiceIndicator";

function ConvoAI() {
  const { state } = useLocation()
  const questions = state?.questions ?? {}
  const job = state?.job ?? {}

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [dataChannel, setDataChannel] = useState(null);
  const peerConnection = useRef(null);
  const audioElement = useRef(null);
  const responseStartTime = useRef(null);

  const formattedQuestions = Object.entries(questions)
    .map(([category, qList]) => `${category}:\n${qList.map(q => `- ${q}`).join("\n")}`)
    .join("\n\n")

  async function startSession() {
    const tokenResponse = await fetch("http://localhost:8000/interview/token");
    const data = await tokenResponse.json();
    const EPHEMERAL_KEY = data.value;

    const pc = new RTCPeerConnection();
    audioElement.current = document.createElement("audio");
    audioElement.current.autoplay = true;
    pc.ontrack = (e) => (audioElement.current.srcObject = e.streams[0]);

    const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
    pc.addTrack(ms.getTracks()[0]);

    const dc = pc.createDataChannel("oai-events");
    setDataChannel(dc);

    dc.onopen = () => {
      dc.send(JSON.stringify({
        type: "session.update",
        session: {
          turn_detection: {
            type: "always_listen",
            threshold: 0.5,
            min_speech_duration_ms: 50,
            max_silence_duration_ms: 200
          },
          interrupt_response: true,
          input_audio_noise_reduction: { type: "near_field" }
        }
      }));

      dc.send(JSON.stringify({
        type: "conversation.item.create",
        item: {
          type: "message",
          role: "system",
          content: [{
            type: "input_text",
            text: `You are an interviewer for ${job.company ?? "this company"} for the role of ${job.role ?? "this role"}.
Your task is to ask the candidate the following questions one by one, in order.
Whenever necessary, follow up on their response before moving on.

Start by asking the candidate to introduce themselves and share their motivation to join ${job.company ?? "this company"}.
Then proceed with the questions below.

${formattedQuestions}`
          }]
        }
      }));

      responseStartTime.current = performance.now();
      dc.send(JSON.stringify({ type: "response.create" }));
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const sdpResponse = await fetch(
      `https://api.openai.com/v1/realtime/calls?model=gpt-realtime`,
      {
        method: "POST",
        body: offer.sdp,
        headers: {
          Authorization: `Bearer ${EPHEMERAL_KEY}`,
          "Content-Type": "application/sdp"
        }
      }
    );

    const sdp = await sdpResponse.text();
    await pc.setRemoteDescription({ type: "answer", sdp });
    peerConnection.current = pc;
  }

  function stopSession() {
    if (dataChannel) dataChannel.close();
    if (peerConnection.current) {
      peerConnection.current.getSenders().forEach((s) => s.track?.stop());
      peerConnection.current.close();
    }
    setIsSessionActive(false);
    setDataChannel(null);
    peerConnection.current = null;
  }

  function sendClientEvent(message) {
    if (!dataChannel) return console.error("No data channel", message);
    message.event_id = message.event_id || crypto.randomUUID();
    if (!message.timestamp) message.timestamp = new Date().toLocaleTimeString();
    dataChannel.send(JSON.stringify(message));
  }

  function sendTextMessage(message) {
    sendClientEvent({
      type: "conversation.item.create",
      item: {
        type: "message", role: "user",
        content: [{ type: "input_text", text: message }]
      }
    });
    responseStartTime.current = performance.now();
    sendClientEvent({ type: "response.create" });
  }

  useEffect(() => {
    if (!dataChannel) return;

    dataChannel.addEventListener("message", (e) => {
      const event = JSON.parse(e.data);
      if (event.type === "response.output_text.delta" && responseStartTime.current) {
        const latency = performance.now() - responseStartTime.current;
        console.log("Model latency:", latency.toFixed(2), "ms");
        responseStartTime.current = null;
      }
    });

    dataChannel.addEventListener("message", (e) => {
      const evt = JSON.parse(e.data);
      if (evt.type === "input_audio_buffer.processed") {
        sendClientEvent({ type: "response.create" });
      }
    });

    dataChannel.addEventListener("open", () => setIsSessionActive(true));
  }, [dataChannel]);

  return (
    <div className="voice-container">
      {/* Job context header */}
      {job.role && (
        <div className="voice-context">
          <span className="voice-context__label">Interviewing for</span>
          <span className="voice-context__role">{job.role}</span>
          <span className="voice-context__sep">·</span>
          <span className="voice-context__company">{job.company}</span>
        </div>
      )}

      {/* Animated orb */}
      {isSessionActive && <VoiceIndicator />}

      {/* Session toggle */}
      <button
        className={`session-btn ${isSessionActive ? "session-btn--stop" : "session-btn--start"}`}
        onClick={() => isSessionActive ? stopSession() : startSession()}
      >
        {isSessionActive ? "⏹ End Session" : "🎤 Launch Session"}
      </button>

      {/* Questions preview */}
      {!isSessionActive && Object.keys(questions).length > 0 && (
        <div className="voice-questions">
          {Object.entries(questions).map(([category, qList]) => (
            <div key={category} className="voice-questions__group">
              <p className="voice-questions__category">{category}</p>
              <ul className="voice-questions__list">
                {qList.map((q, i) => (
                  <li key={i} className="voice-questions__item">
                    <span className="voice-questions__num">{String(i + 1).padStart(2, "0")}</span>
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ConvoAI;