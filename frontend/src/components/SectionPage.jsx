import { ShieldCheck } from "lucide-react";

function SectionPage({ title, description }) {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>

        <div className="dashboard-connection-status">
          <span className="online-dot" />
          Backend Online
        </div>
      </header>

      <section className="stats">
        <div className="stat-card">
          <div className="stat-card-icon">
            <ShieldCheck size={20} />
          </div>

          <div>
            <div className="stat-card-label">
              API-Sentinel
            </div>

            <div className="stat-card-value">
              Active
            </div>

            <div className="stat-card-description">
              Security monitoring is operational.
            </div>
          </div>
        </div>
      </section>

      <section className="threat-overview">
        <div className="threat-overview-header">
          <div>
            <h2>{title}</h2>
            <p>
              This section is ready for its API-Sentinel
              security functionality.
            </p>
          </div>

          <div className="environment">
            <span className="environment-dot" />
            <span>READY</span>
          </div>
        </div>

        <div className="threat-overview-body">
          <p>
            The navigation is working correctly. This page can
            now be connected to its corresponding backend data.
          </p>
        </div>
      </section>
    </div>
  );
}

export default SectionPage;