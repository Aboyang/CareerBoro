import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./SettingsPanel.css";

// ── localStorage helpers ──────────────────────────────────────────────────────
function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn("[Settings] localStorage write failed:", e);
  }
}

const LS = {
  EXP:     "settings:expLevels",
  ROLES:   "settings:roles",
  LOCS:    "settings:locations",
  TIME:    "settings:fetchTime",
  PROFILE: "settings:profile",
};

// ── Sub-component: Tag input ──────────────────────────────────────────────────
function TagInput({ label, placeholder, tags, onChange }) {
  const [input, setInput] = useState("");

  const addTag = (value) => {
    const trimmed = value.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
    }
    setInput("");
  };

  const removeTag = (tag) => onChange(tags.filter((t) => t !== tag));

  const handleKeyDown = (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(input);
    } else if (e.key === "Backspace" && !input && tags.length) {
      removeTag(tags[tags.length - 1]);
    }
  };

  return (
    <div className="sp-field">
      <label className="sp-label">{label}</label>
      <div className="sp-tag-box">
        {tags.map((tag) => (
          <span key={tag} className="sp-tag">
            {tag}
            <button className="sp-tag-remove" onClick={() => removeTag(tag)}>✕</button>
          </span>
        ))}
        <input
          className="sp-tag-input"
          value={input}
          placeholder={tags.length === 0 ? placeholder : ""}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => input && addTag(input)}
        />
      </div>
      <p className="sp-hint">Press Enter or comma to add</p>
    </div>
  );
}

// ── Sub-component: Experience level pills ─────────────────────────────────────
const EXP_LEVELS = ["Internship", "Full-time", "Contract"];

function ExperienceSelector({ selected, onChange }) {
  const toggle = (level) =>
    onChange(
      selected.includes(level)
        ? selected.filter((l) => l !== level)
        : [...selected, level]
    );

  return (
    <div className="sp-field">
      <label className="sp-label">Experience level</label>
      <div className="sp-pills">
        {EXP_LEVELS.map((level) => (
          <button
            key={level}
            className={`sp-pill ${selected.includes(level) ? "sp-pill--active" : ""}`}
            onClick={() => toggle(level)}
          >
            {level}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Sub-component: Resume upload ──────────────────────────────────────────────
function ResumeUpload({ onParsed, alreadyParsed }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  // If a profile was loaded from localStorage, show done state immediately
  const isDone = parsed || (alreadyParsed && !file);

  const ACCEPTED = ".pdf,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document";

  const handleFile = (f) => { setFile(f); setParsed(false); };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post("http://localhost:8000/resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const data = JSON.parse(res.data.resume_context);
      onParsed(data);
      setParsed(true);
    } catch (err) {
      console.error("Resume upload failed:", err);
    }
    setLoading(false);
  };

  return (
    <div className="sp-field">
      <label className="sp-label">Resume</label>
      <div
        className={`sp-dropzone ${dragging ? "sp-dropzone--drag" : ""} ${isDone ? "sp-dropzone--done" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !file && !isDone && inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {isDone ? (
          <span className="sp-dropzone__status sp-dropzone__status--done">✓ Resume parsed</span>
        ) : loading ? (
          <span className="sp-dropzone__status">Parsing resume…</span>
        ) : file ? (
          <span className="sp-dropzone__status">{file.name}</span>
        ) : (
          <span className="sp-dropzone__status sp-dropzone__status--empty">
            Drop your resume here, or <u>click to upload</u>
          </span>
        )}

        {file && !isDone && (
          <div className="sp-dropzone__actions" onClick={(e) => e.stopPropagation()}>
            <button className="sp-icon-btn sp-icon-btn--primary" onClick={submit} disabled={loading}>
              {loading ? "…" : "↑"}
            </button>
            <button className="sp-icon-btn" onClick={() => { setFile(null); setParsed(false); }}>✕</button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sub-component: Parsed profile viewer ──────────────────────────────────────
function ProfileViewer({ profile }) {
  if (!profile) return null;

  return (
    <div className="sp-profile">
      <div className="sp-profile__header">
        <span className="sp-label">Extracted profile</span>
      </div>

      <div className="sp-profile__meta">
        {profile.University && (
          <div className="sp-profile__meta-item">
            <span className="sp-profile__meta-label">University</span>
            <span className="sp-profile__meta-value">{profile.University}</span>
          </div>
        )}
        {profile.Grade && (
          <div className="sp-profile__meta-item">
            <span className="sp-profile__meta-label">Grade</span>
            <span className="sp-profile__meta-value">{profile.Grade}</span>
          </div>
        )}
      </div>

      {profile["Career Experience"]?.length > 0 && (
        <details className="sp-profile__section">
          <summary className="sp-profile__summary">Career Experience <span className="sp-profile__count">{profile["Career Experience"].length}</span></summary>
          <div className="sp-profile__entries">
            {profile["Career Experience"].map((c, i) => (
              <div key={i} className="sp-profile__entry">
                <div className="sp-profile__entry-header">
                  <strong>{c.role}</strong>
                  <span className="sp-profile__entry-date">{c.date}</span>
                </div>
                <p className="sp-profile__entry-desc">{c.description}</p>
              </div>
            ))}
          </div>
        </details>
      )}

      {profile["Project Experience"]?.length > 0 && (
        <details className="sp-profile__section">
          <summary className="sp-profile__summary">Project Experience <span className="sp-profile__count">{profile["Project Experience"].length}</span></summary>
          <div className="sp-profile__entries">
            {profile["Project Experience"].map((p, i) => (
              <div key={i} className="sp-profile__entry">
                <div className="sp-profile__entry-header">
                  <strong>{p.role}</strong>
                  <span className="sp-profile__entry-date">{p.date}</span>
                </div>
                <p className="sp-profile__entry-desc">{p.description}</p>
              </div>
            ))}
          </div>
        </details>
      )}

      {profile["Technical Skillset"]?.length > 0 && (
        <details className="sp-profile__section">
          <summary className="sp-profile__summary">Technical Skills <span className="sp-profile__count">{profile["Technical Skillset"].length}</span></summary>
          <div className="sp-profile__chips">
            {profile["Technical Skillset"].map((s, i) => (
              <span key={i} className="sp-chip sp-chip--tech">{s}</span>
            ))}
          </div>
        </details>
      )}

      {profile["Softskill Displayed"]?.length > 0 && (
        <details className="sp-profile__section">
          <summary className="sp-profile__summary">Soft Skills <span className="sp-profile__count">{profile["Softskill Displayed"].length}</span></summary>
          <div className="sp-profile__chips">
            {profile["Softskill Displayed"].map((s, i) => (
              <span key={i} className="sp-chip sp-chip--soft">{s}</span>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

// ── Main: SettingsPanel ───────────────────────────────────────────────────────
export default function SettingsPanel({ open, onClose }) {
  const [expLevels, setExpLevels] = useState(() => load(LS.EXP, []));
  const [roles,     setRoles]     = useState(() => load(LS.ROLES, []));
  const [locations, setLocations] = useState(() => load(LS.LOCS, []));
  const [fetchTime, setFetchTime] = useState(() => load(LS.TIME, "08:00"));
  const [profile,   setProfile]   = useState(() => load(LS.PROFILE, null));
  const [saved, setSaved] = useState(false);

  // Persist each field on change
  const setAndSaveExp  = (v) => { setExpLevels(v); save(LS.EXP, v); };
  const setAndSaveRoles = (v) => { setRoles(v);    save(LS.ROLES, v); };
  const setAndSaveLocs  = (v) => { setLocations(v); save(LS.LOCS, v); };
  const setAndSaveTime  = (v) => { setFetchTime(v); save(LS.TIME, v); };

  const handleParsed = (data) => {
    setProfile(data);
    save(LS.PROFILE, data);
  };

  const handleClearProfile = () => {
    setProfile(null);
    localStorage.removeItem(LS.PROFILE);
  };

  // Close on Escape
  useEffect(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Lock body scroll
  useEffect(() => {
    if (open) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const handleSave = () => {
    // All fields already auto-saved to localStorage on change.
    // Wire to backend here if needed:
    // await axios.post("http://localhost:8000/settings", { expLevels, roles, locations, fetchTime });
    console.log("[Settings] Persisted:", { expLevels, roles, locations, fetchTime });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!open) return null;

  return (
    <div className="sp-overlay" onClick={onClose}>
      <div className="sp-drawer" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">

        {/* Header */}
        <div className="sp-header">
          <div>
            <h3 className="sp-title">Settings</h3>
            <p className="sp-subtitle">Configure your job search preferences</p>
          </div>
          <button className="sp-close" onClick={onClose}>✕</button>
        </div>

        {/* Scrollable body */}
        <div className="sp-body">

          {/* ── Section: Filters ── */}
          <section className="sp-section">
            <p className="sp-section-title">Job Filters</p>

            <ExperienceSelector selected={expLevels} onChange={setAndSaveExp} />

            <TagInput
              label="Roles"
              placeholder="e.g. Frontend Engineer, ML Engineer…"
              tags={roles}
              onChange={setAndSaveRoles}
            />

            <TagInput
              label="Locations"
              placeholder="e.g. Singapore, Remote…"
              tags={locations}
              onChange={setAndSaveLocs}
            />
          </section>

          {/* ── Section: Schedule ── */}
          <section className="sp-section">
            <p className="sp-section-title">Automated Fetch</p>
            <div className="sp-field">
              <label className="sp-label">Daily fetch time</label>
              <div className="sp-time-row">
                <input
                  type="time"
                  className="sp-time-input"
                  value={fetchTime}
                  onChange={(e) => setAndSaveTime(e.target.value)}
                />
                <span className="sp-hint">Jobs will be fetched automatically at this time each day</span>
              </div>
            </div>
          </section>

          <section className="sp-section">
            <p className="sp-section-title">Resume</p>
            <ResumeUpload onParsed={handleParsed} alreadyParsed={!!profile} />
            {profile && (
              <>
                <ProfileViewer profile={profile} />
                <button className="sp-btn sp-btn--ghost sp-btn--sm" onClick={handleClearProfile}>
                  ✕ Clear resume
                </button>
              </>
            )}
          </section>
        </div>

        {/* Footer */}
        <div className="sp-footer">
          <button className="sp-btn sp-btn--ghost" onClick={onClose}>Cancel</button>
          <button className="sp-btn sp-btn--primary" onClick={handleSave}>
            {saved ? "✓ Saved" : "Save settings"}
          </button>
        </div>

      </div>
    </div>
  );
}