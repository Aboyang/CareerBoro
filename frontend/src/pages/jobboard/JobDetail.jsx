import { useEffect } from "react";
import "./JobBoard.css"

export default function JobDetail({ job, onClose }) {
  // Close on Escape
  useEffect(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Prevent body scroll while open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  if (!job) return null;

  const refs = Array.isArray(job.webpages_read)
    ? job.webpages_read
    : job.webpages_read
    ? [job.webpages_read]
    : [];

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div
        className="detail-panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={`${job.role} at ${job.company}`}
      >
        {/* Close */}
        <button className="detail-close" onClick={onClose} aria-label="Close">
          ✕
        </button>

        {/* Hero */}
        <div className="detail-hero">
          <div className="detail-badge">{job.company?.[0] ?? "?"}</div>
          <div>
            <h2 className="detail-role">{job.role}</h2>
            <p className="detail-company">{job.company}</p>
          </div>
        </div>

        <div className="detail-divider" />

        {/* Body */}
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
                    <a href={ref} target="_blank" rel="noopener noreferrer" className="detail-ref-link">
                      {ref}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* Actions */}
        <div className="detail-actions">
          <a
            href={job.apply_link}
            target="_blank"
            rel="noopener noreferrer"
            className="detail-apply-btn"
          >
            Apply Now ↗
          </a>
          <button className="detail-interview-btn" disabled>
            🎤 Practice Interview
            <span className="detail-interview-badge">Coming Soon</span>
          </button>
        </div>
      </div>
    </div>
  );
}