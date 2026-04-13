
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import "./JobBoard.css"

function loadResumeContext() {
  try {
    const raw = localStorage.getItem("settings:profile")
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

// ── Interview prep modal (shown after clicking Practice Interview) ─────────────
function InterviewPrepModal({ job, onClose }) {
  const navigate = useNavigate()
  const [step, setStep] = useState("idle") // idle | loading | ready | error
  const [questions, setQuestions] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchQuestions()
  }, [])

  async function fetchQuestions() {
    setStep("loading")
    const resumeContext = loadResumeContext()

    try {
      const res = await fetch("http://localhost:8000/interview/questions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: job.role,
          company: job.company,
          job_desc: job.job_desc,
          resume_context: resumeContext,
        }),
      })
      const data = await res.json()
      try {
        const parsed =
          typeof data.questions === "string"
            ? JSON.parse(data.questions)
            : data.questions

        setQuestions(parsed)
        setStep("ready")
      } catch (e) {
        console.error("JSON parse failed:", e)
        setError("Invalid question format from server.")
        setStep("error")
      }
    } catch (err) {
      console.error("Failed to fetch questions:", err)
      setError("Failed to generate questions. Please try again.")
      setStep("error")
    }
  }

  function beginInterview() {
    navigate("/interview", { state: { questions, job } })
  }

  return (
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 999999,
        background: "rgba(0,0,0,0.85)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "24px",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#1f2333",
          border: "1px solid rgba(99,179,237,0.35)",
          borderRadius: "16px",
          width: "100%", maxWidth: "600px", maxHeight: "80vh",
          overflowY: "auto", padding: "28px", position: "relative",
          display: "flex", flexDirection: "column", gap: "20px",
        }}
      >
        {/* Header */}
        <div>
          <button className="detail-close" onClick={onClose}>✕</button>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "4px" }}>
            <div className="detail-badge" style={{ width: "40px", height: "40px", fontSize: "1rem" }}>
              {job.company?.[0] ?? "?"}
            </div>
            <div>
              <h3 className="detail-role" style={{ fontSize: "1rem" }}>Practice Interview</h3>
              <p className="detail-company">{job.role} · {job.company}</p>
            </div>
          </div>
        </div>

        <div className="detail-divider" />

        {/* Loading */}
        {step === "loading" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px", padding: "24px 0" }}>
            <div className="interview-spinner" />
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              Generating tailored questions…
            </p>
          </div>
        )}

        {/* Error */}
        {step === "error" && (
          <div style={{ textAlign: "center", padding: "16px 0" }}>
            <p style={{ color: "#fc8181", fontSize: "0.85rem", marginBottom: "12px" }}>{error}</p>
            <button className="detail-apply-btn" onClick={fetchQuestions}>Retry</button>
          </div>
        )}

        {/* Questions ready */}
        {step === "ready" && questions && (
          <>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {Object.entries(questions).map(([category, qList]) => (
                <div key={category}>
                  <p style={{
                    fontSize: "0.63rem", fontFamily: "var(--font-mono)",
                    textTransform: "uppercase", letterSpacing: "0.1em",
                    color: "var(--accent)", marginBottom: "8px"
                  }}>
                    {category}
                  </p>
                  <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "6px" }}>
                    {qList.map((q, i) => (
                      <li key={i} style={{
                        fontSize: "0.8rem", color: "var(--text-secondary)",
                        lineHeight: "1.55", padding: "8px 12px",
                        background: "var(--surface)", borderRadius: "8px",
                        border: "1px solid var(--border)",
                        display: "flex", gap: "10px", alignItems: "flex-start"
                      }}>
                        <span style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: "0.65rem", marginTop: "2px", flexShrink: 0 }}>
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        {q}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div style={{ display: "flex", gap: "10px", paddingTop: "8px", borderTop: "1px solid var(--border)" }}>
              <button className="detail-apply-btn" onClick={beginInterview}>
                🎤 Begin Interview
              </button>
              <button className="detail-interview-btn" onClick={onClose}>
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ── Main JobDetail ────────────────────────────────────────────────────────────
export default function JobDetail({ job, onClose }) {
  const [showPrepModal, setShowPrepModal] = useState(false)

  useEffect(() => {
    const handler = (e) => e.key === "Escape" && (showPrepModal ? setShowPrepModal(false) : onClose())
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [onClose, showPrepModal])

  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => { document.body.style.overflow = "" }
  }, [])

  if (!job) return null

  const refs = Array.isArray(job.webpages_read)
    ? job.webpages_read.map(r => r?.url ?? r)
    : job.webpages_read ? [job.webpages_read] : []

  const content = (
    <>
      <div
        className="detail-overlay"
        onClick={onClose}
        style={{
          position: "fixed", inset: 0, zIndex: 99999,
          background: "rgba(0,0,0,0.8)",
          display: "flex", alignItems: "center", justifyContent: "center",
          padding: "24px",
        }}
      >
        <div
          className="detail-panel"
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          style={{
            background: "#1f2333",
            border: "1px solid rgba(99,179,237,0.35)",
            borderRadius: "16px", width: "100%", maxWidth: "640px",
            maxHeight: "85vh", overflowY: "auto", padding: "28px",
            position: "relative",
          }}
        >
          <button className="detail-close" onClick={onClose} aria-label="Close">✕</button>

          <div className="detail-hero">
            <div className="detail-badge">{job.company?.[0] ?? "?"}</div>
            <div>
              <h2 className="detail-role">{job.role}</h2>
              <p className="detail-company">{job.company}</p>
            </div>
          </div>

          <div className="detail-divider" />

          <div className="detail-body">
            <section className="detail-section">
              <h4 className="detail-label">Job Description</h4>
              <p className="detail-text">{job.job_desc || "No description provided."}</p>
            </section>

            <section className="detail-section">
              <h4 className="detail-label">Research Notes</h4>
              <p className="detail-text">{job.research || "No research notes."}</p>
            </section>

            {refs.length > 0 && (
              <section className="detail-section">
                <h4 className="detail-label">Reference Links</h4>
                <ul className="detail-refs">
                  {refs.map((ref, i) => (
                    <li key={i}>
                      <a href={ref} target="_blank" rel="noopener noreferrer" className="detail-ref-link">{ref}</a>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>

          <div className="detail-actions">
            {job.apply_link ? (
              <a href={job.apply_link} target="_blank" rel="noopener noreferrer" className="detail-apply-btn">
                Apply Now ↗
              </a>
            ) : (
              <span className="detail-apply-btn job-card__apply-btn--disabled">No link</span>
            )}
            <button
              className="detail-interview-btn detail-interview-btn--active"
              onClick={() => setShowPrepModal(true)}
            >
              🎤 Practice Interview
            </button>
          </div>
        </div>
      </div>

      {/* Interview prep modal sits on top */}
      {showPrepModal && (
        <InterviewPrepModal
          job={job}
          onClose={() => setShowPrepModal(false)}
        />
      )}
    </>
  )

  return createPortal(content, document.body)
}