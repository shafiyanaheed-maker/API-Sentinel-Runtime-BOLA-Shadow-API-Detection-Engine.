import {
  Activity,
  Box,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react";

const cardIcons = {
  "BOLA Threats": LockKeyhole,
  "BFLA Threats": ShieldCheck,
  "Shadow APIs": Box,
  Requests: Activity,
};

const cardTypes = {
  "BOLA Threats": "danger",
  "BFLA Threats": "warning",
  "Shadow APIs": "purple",
  Requests: "info",
};

function StatCard({ title, value, description }) {
  const Icon = cardIcons[title] || Activity;
  const type = cardTypes[title] || "info";

  return (
    <div className={`stat-card stat-card-${type}`}>
      <div className="stat-card-top">
        <div className="stat-card-icon">
          <Icon size={17} strokeWidth={2} />
        </div>

        <span className="stat-card-status">
          {title === "Requests" ? "MONITORED" : "DETECTED"}
        </span>
      </div>

      <div className="stat-card-content">
        <div className="stat-value">{value}</div>

        <h3>{title}</h3>

        <p>{description}</p>
      </div>
    </div>
  );
}

export default StatCard;