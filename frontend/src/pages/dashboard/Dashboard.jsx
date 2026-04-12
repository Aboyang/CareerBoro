import Chat from "../chat/Chat";
import JobBoard from "../jobboard/JobBoard";
import "./Dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard">
      
      {/* LEFT: JobBoard */}
      <div className="dashboard-left">
        <div className="placeholder">
            <JobBoard />
        </div>
      </div>

      {/* RIGHT: Chat */}
      <div className="dashboard-right">
        <Chat />
      </div>

    </div>
  );
}