import { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import ThreatTable from "../components/ThreatTable";
import ThreatOverview from "../components/ThreatOverview";
import APIInventory from "../components/APIInventory";
import { analyzeRequest, checkHealth } from "../services/api";

function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    bolaThreats: 0,
    bflaThreats: 0,
    shadowApis: 0,
    requests: 0,
  });

  const [backendStatus, setBackendStatus] = useState("Checking");

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      try {
        await checkHealth();

        if (isMounted) {
          setBackendStatus("Online");
        }

        const result = await analyzeRequest({
          method: "GET",
          path: "/users/105",
          authenticated_user_id: 102,
          user_role: "user",
          client_id: "dashboard-client",
        });

        if (!isMounted) {
          return;
        }

        const threats = result.analysis?.threats || [];

        const bolaThreats = threats.filter(
          (threat) => threat.type === "BOLA"
        ).length;

        const bflaThreats = threats.filter(
          (threat) => threat.type === "BFLA"
        ).length;

        setDashboardData({
          bolaThreats,
          bflaThreats,
          shadowApis: 0,
          requests: 1,
        });
      } catch (error) {
        console.error("Dashboard API error:", error);

        if (isMounted) {
          setBackendStatus("Offline");
        }
      }
    }

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Security Dashboard</h1>
          <p>Real-time API security monitoring</p>
        </div>

        <div className="dashboard-connection-status">
          <span
            className={`online-dot ${
              backendStatus === "Offline" ? "status-offline" : ""
            }`}
          />

          {backendStatus === "Checking"
            ? "Connecting..."
            : `Backend ${backendStatus}`}
        </div>
      </header>

      <section className="stats">
        <StatCard
          title="BOLA Threats"
          value={dashboardData.bolaThreats}
          description="Object-level attacks detected"
        />

        <StatCard
          title="BFLA Threats"
          value={dashboardData.bflaThreats}
          description="Function-level attacks detected"
        />

        <StatCard
          title="Shadow APIs"
          value={dashboardData.shadowApis}
          description="Undocumented APIs detected"
        />

        <StatCard
          title="Requests"
          value={dashboardData.requests}
          description="Requests analyzed"
        />
      </section>

      <ThreatOverview />

      <ThreatTable />

      <APIInventory />
    </div>
  );
}

export default Dashboard;