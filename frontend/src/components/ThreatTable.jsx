function ThreatTable() {
  const threats = [
    {
      type: "BOLA",
      endpoint: "/users/105",
      severity: "HIGH",
      status: "Blocked",
    },
    {
      type: "BFLA",
      endpoint: "/admin/users",
      severity: "HIGH",
      status: "Blocked",
    },
  ];

  return (
    <div className="threat-table">
      <h2>Recent Threats</h2>

      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Endpoint</th>
            <th>Severity</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {threats.map((threat, index) => (
            <tr key={index}>
              <td>{threat.type}</td>
              <td>{threat.endpoint}</td>
              <td>{threat.severity}</td>
              <td>{threat.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ThreatTable;