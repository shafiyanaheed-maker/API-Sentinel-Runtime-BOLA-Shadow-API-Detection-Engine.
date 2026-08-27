import StatCard from "../components/StatCard";
import ThreatTable from "../components/ThreatTable";

function Dashboard() {
  return (
    <div className="dashboard">
      <header>
        <h1>Security Dashboard</h1>
        <p>Real-time API security monitoring</p>
      </header>

      <section className="stats">
        <StatCard
          title="BOLA Threats"
          value="1"
          description="Object-level attacks detected"
        />

        <StatCard
          title="BFLA Threats"
          value="1"
          description="Function-level attacks detected"
        />

        <StatCard
          title="Shadow APIs"
          value="0"
          description="Undocumented APIs detected"
        />

        <StatCard
          title="Requests"
          value="10"
          description="Requests analyzed"
        />
      </section>

      <ThreatTable />
    </div>
  );
}

export default Dashboard;