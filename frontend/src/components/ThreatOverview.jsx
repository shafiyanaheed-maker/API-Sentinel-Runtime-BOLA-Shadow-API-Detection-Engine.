const threatData = [
  {
    label: "BOLA",
    value: 1,
    percentage: 25,
    description: "Object-level attacks",
  },
  {
    label: "BFLA",
    value: 1,
    percentage: 25,
    description: "Function-level attacks",
  },
  {
    label: "Shadow APIs",
    value: 0,
    percentage: 0,
    description: "Undocumented endpoints",
  },
  {
    label: "Requests",
    value: 10,
    percentage: 100,
    description: "Requests analyzed",
  },
];

function ThreatOverview() {
  return (
    <section className="threat-overview">
      <div className="section-heading">
        <div>
          <h2>Threat Overview</h2>
          <p>Runtime security activity</p>
        </div>

        <div className="overview-status">
          <span className="online-dot"></span>
          Monitoring
        </div>
      </div>

      <div className="threat-bars">
        {threatData.map((item) => (
          <div className="threat-bar-item" key={item.label}>
            <div className="threat-bar-header">
              <div>
                <strong>{item.label}</strong>
                <span>{item.description}</span>
              </div>

              <strong className="threat-bar-value">{item.value}</strong>
            </div>

            <div className="threat-bar-track">
              <div
                className="threat-bar-fill"
                style={{ width: `${item.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default ThreatOverview;