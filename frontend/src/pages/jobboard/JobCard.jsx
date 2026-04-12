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

  return (
    <div
      className={`job-card ${hovered ? "job-card--hovered" : ""}`}
      onClick={() => onClick(job)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick(job)}
      aria-label={`View details for ${job.role} at ${job.company}`}
    >
      {/* Header */}
      <div className="job-card__header">
        <div className="job-card__badge">{job.company?.[0] ?? "?"}</div>
        <div className="job-card__titles">
          <h3 className="job-card__role">{job.role}</h3>
          <p className="job-card__company">{job.company}</p>
        </div>
      </div>

      <div className="job-card__divider" />

      {/* Description */}
      <section className="job-card__section">
        <span className="job-card__label">Description</span>
        <p className="job-card__text">{truncate(job.job_desc, TRUNCATE_DESC)}</p>
      </section>

      {/* Research */}
      <section className="job-card__section">
        <span className="job-card__label">Research</span>
        <p className="job-card__text">{truncate(job.research, TRUNCATE_RESEARCH)}</p>
      </section>

      {/* Refs */}
      <section className="job-card__section">
        <span className="job-card__label">References</span>
        <p className="job-card__text job-card__text--ref">
          {truncate(
            Array.isArray(job.webpages_read)
              ? job.webpages_read.join("  ·  ")
              : job.webpages_read,
            TRUNCATE_REFS
          )}
        </p>
      </section>

      {/* Footer */}
      <div className="job-card__footer">
        <a
          href={job.apply_link}
          target="_blank"
          rel="noopener noreferrer"
          className="job-card__apply-btn"
          onClick={(e) => e.stopPropagation()}
        >
          Apply ↗
        </a>
        <span className="job-card__expand-hint">Click to expand</span>
      </div>
    </div>
  );
}