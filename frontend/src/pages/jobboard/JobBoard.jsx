import { useState, useEffect, useRef } from "react";
import JobCard from "./JobCard";
import JobDetail from "./JobDetail";
import SettingsPanel from "../settings/SettingsPanel";
import "./JobBoard.css";

export default function JobBoard() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [connected, setConnected] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = () => {
    const ws = new WebSocket("ws://localhost:8000/jobs/ws");
    wsRef.current = ws;
    ws.onopen = () => { setConnected(true); clearTimeout(reconnectTimer.current); };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data?.type === "ping") return;
      setJobs(data);
    };
    ws.onerror = (err) => console.error("[JobBoard] WebSocket error:", err);
    ws.onclose = () => {
      setConnected(false);
      reconnectTimer.current = setTimeout(connect, 3000);
    };
  };

  useEffect(() => {
    connect();
    return () => { clearTimeout(reconnectTimer.current); wsRef.current?.close(); };
  }, []);

  console.log("selectedJob:", selectedJob)

  return (
    <div className="jobboard">
      <div className="jobboard__header">
        <div className="jobboard__header-left">
          <h2 className="jobboard__title">Job Listings</h2>
          <span className="jobboard__count">{jobs.length} roles</span>
          {!connected && <span className="jobboard__status">⚠ Reconnecting…</span>}
        </div>
        <button className="jobboard__settings-btn" onClick={() => setSettingsOpen(true)} aria-label="Open settings">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          Settings
        </button>
      </div>

      <div className="jobboard__grid">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} onClick={setSelectedJob} />
        ))}
      </div>

      {selectedJob && <JobDetail job={selectedJob} onClose={() => setSelectedJob(null)} />}
      <SettingsPanel open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
