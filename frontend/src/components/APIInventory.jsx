const apiInventory = [
  {
    method: "GET",
    endpoint: "/users/{id}",
    status: "Protected",
    risk: "High",
    discovered: "Known",
  },
  {
    method: "GET",
    endpoint: "/profiles/{id}",
    status: "Protected",
    risk: "Medium",
    discovered: "Known",
  },
  {
    method: "POST",
    endpoint: "/users",
    status: "Protected",
    risk: "Low",
    discovered: "Known",
  },
  {
    method: "GET",
    endpoint: "/admin/users",
    status: "Protected",
    risk: "Critical",
    discovered: "Known",
  },
  {
    method: "GET",
    endpoint: "/legacy/reports",
    status: "Unprotected",
    risk: "High",
    discovered: "Shadow",
  },
];

function APIInventory() {
  return (
    <section className="api-inventory">
      <div className="section-heading">
        <div>
          <h2>API Inventory</h2>
          <p>Discovered and monitored API endpoints</p>
        </div>

        <span className="inventory-count">
          {apiInventory.length} endpoints
        </span>
      </div>

      <div className="inventory-table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Method</th>
              <th>Endpoint</th>
              <th>Status</th>
              <th>Risk</th>
              <th>Discovery</th>
            </tr>
          </thead>

          <tbody>
            {apiInventory.map((api, index) => (
              <tr key={`${api.method}-${api.endpoint}-${index}`}>
                <td>
                  <span className={`method method-${api.method.toLowerCase()}`}>
                    {api.method}
                  </span>
                </td>

                <td className="api-endpoint">{api.endpoint}</td>

                <td>
                  <span
                    className={`api-status ${
                      api.status === "Protected"
                        ? "status-protected"
                        : "status-unprotected"
                    }`}
                  >
                    {api.status}
                  </span>
                </td>

                <td>
                  <span
                    className={`risk risk-${api.risk.toLowerCase()}`}
                  >
                    {api.risk}
                  </span>
                </td>

                <td>
                  <span
                    className={`discovery discovery-${api.discovered.toLowerCase()}`}
                  >
                    {api.discovered}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default APIInventory;