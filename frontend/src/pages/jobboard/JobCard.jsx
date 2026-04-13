import { useState } from "react";
import "./JobBoard.css"

const TRUNCATE_DESC = 120;
const TRUNCATE_RESEARCH = 100;
const TRUNCATE_REFS = 80;

function truncate(text, len) {
  if (!text) return "—";
  return text.length > len ? text.slice(0, len) + "…" : text;
}

export default function JobCard({ job, onClick }) {
  const [hovered, setHovered] = useState(false);

  const handleClick = (e) => {
    e.stopPropagation()
    onClick(job)
  }

  return (
    <div
      className={`job-card ${hovered ? "job-card--hovered" : ""}`}
      onClick={handleClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && handleClick(e)}
      aria-label={`View details for ${job.role} at ${job.company}`}
    >
      <div className="job-card__header">
        <div className="job-card__badge">{job.company?.[0] ?? "?"}</div>
        <div className="job-card__titles">
          <h3 className="job-card__role">{job.role}</h3>
          <p className="job-card__company">{job.company}</p>
        </div>
      </div>

      <div className="job-card__divider" />

      <section className="job-card__section">
        <span className="job-card__label">Description</span>
        <p className="job-card__text">{truncate(job.job_desc, TRUNCATE_DESC)}</p>
      </section>

      <section className="job-card__section">
        <span className="job-card__label">Research</span>
        <p className="job-card__text">{truncate(job.research, TRUNCATE_RESEARCH)}</p>
      </section>

      <section className="job-card__section">
        <span className="job-card__label">References</span>
        <p className="job-card__text job-card__text--ref">
          {truncate(
            Array.isArray(job.webpages_read)
              ? job.webpages_read.map(w => w.url ?? w).join("  ·  ")
              : job.webpages_read,
            TRUNCATE_REFS
          )}
        </p>
      </section>

      <div className="job-card__footer">
        {job.apply_link ? (
          <a
            href={job.apply_link}
            target="_blank"
            rel="noopener noreferrer"
            className="job-card__apply-btn"
            onClick={(e) => e.stopPropagation()}
          >
            Apply ↗
          </a>
        ) : (
          <span className="job-card__apply-btn job-card__apply-btn--disabled">No link</span>
        )}
        <span className="job-card__expand-hint">Click to expand</span>
      </div>
    </div>
  );
}