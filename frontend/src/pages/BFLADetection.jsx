import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

import { analyzeRequest } from "../services/api";
import "./SecurityPages.css";

function saveThreat(result, request) {
  const threats = result?.analysis?.threats || [];

  if (threats.length === 0) {
    return;
  }

  const existing = JSON.parse(
    localStorage.getItem("apiSentinelThreats") || "[]"
  );

  const newThreats = threats.map((threat) => ({
    ...threat,
    endpoint: request.path,
    detectedAt: new Date().toISOString(),
    status: "Blocked",
  }));

  localStorage.setItem(
    "apiSentinelThreats",
    JSON.stringify([...newThreats, ...existing].slice(0, 50))
  );
}

function BFLADetection() {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/admin/users");
  const [role, setRole] = useState("user");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleScan(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await analyzeRequest({
        method,
        path,
        authenticated_user_id: 102,
        user_role: role,
        client_id: "bfla-detection-page",
      });

      setResult(response);

      saveThreat(response, {
        method,
        path,
      });
    } catch (scanError) {
      console.error("BFLA scan failed:", scanError);
      setError(
        "Unable to connect to the API-Sentinel backend. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const threats = result?.analysis?.threats || [];

  const bflaThreats = threats.filter(
    (threat) => threat.type === "BFLA"
  );

  return (
    <div className="security-page">
      <header className="security-page-header">
        <div>
          <div className="security-page-title-row">
            <div className="security-page-icon bfla-icon">
              <ShieldCheck size={23} />
            </div>

            <div>
              <h1>BFLA Detection</h1>
              <p>
                Detect unauthorized function-level API access
                based on user roles.
              </p>
            </div>
          </div>
        </div>

        <div className="security-page-status">
          <span className="online-dot" />
          Detection Engine Active
        </div>
      </header>

      <section className="security-info-grid">
        <div className="security-info-card">
          <span className="security-info-label">THREAT TYPE</span>
          <strong>BFLA</strong>
          <p>Broken Function Level Authorization</p>
        </div>

        <div className="security-info-card">
          <span className="security-info-label">SEVERITY</span>
          <strong className="severity-high">HIGH</strong>
          <p>Unauthorized function access</p>
        </div>

        <div className="security-info-card">
          <span className="security-info-label">ROLE CHECK</span>
          <strong>Active</strong>
          <p>Runtime role authorization</p>
        </div>
      </section>

      <section className="security-panel">
        <div className="security-panel-header">
          <div>
            <h2>Test Function Access</h2>
            <p>
              Send a request through the runtime BFLA detection
              engine.
            </p>
          </div>

          <ShieldAlert size={22} />
        </div>

        <form
          className="security-form"
          onSubmit={handleScan}
        >
          <div className="security-form-row">
            <label>
              HTTP Method
              <select
                value={method}
                onChange={(event) =>
                  setMethod(event.target.value)
                }
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
                <option value="DELETE">DELETE</option>
              </select>
            </label>

            <label>
              API Endpoint
              <input
                value={path}
                onChange={(event) =>
                  setPath(event.target.value)
                }
                placeholder="/admin/users"
              />
            </label>

            <label>
              User Role
              <select
                value={role}
                onChange={(event) =>
                  setRole(event.target.value)
                }
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </label>
          </div>

          <div className="security-form-actions">
            <span className="security-hint">
              Try the <strong>user</strong> role against{" "}
              <strong>/admin/users</strong> to demonstrate
              BFLA.
            </span>

            <button
              type="submit"
              className="security-primary-button"
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Request"}
            </button>
          </div>
        </form>
      </section>

      {error && (
        <section className="security-result error-result">
          <AlertTriangle size={22} />
          <div>
            <strong>Analysis Failed</strong>
            <p>{error}</p>
          </div>
        </section>
      )}

      {result && !error && (
        <section className="security-panel">
          <div className="security-panel-header">
            <div>
              <h2>Analysis Result</h2>
              <p>
                Runtime response from the API-Sentinel analyzer.
              </p>
            </div>

            {bflaThreats.length > 0 ? (
              <div className="result-badge danger">
                <AlertTriangle size={15} />
                BFLA Detected
              </div>
            ) : (
              <div className="result-badge safe">
                <CheckCircle2 size={15} />
                No BFLA Detected
              </div>
            )}
          </div>

          <div className="result-grid">
            <div>
              <span>REQUEST</span>
              <strong>
                {method} {path}
              </strong>
            </div>

            <div>
              <span>ROLE</span>
              <strong>{role}</strong>
            </div>

            <div>
              <span>OVERALL STATUS</span>
              <strong>
                {result.allowed ? "Allowed" : "Blocked"}
              </strong>
            </div>

            <div>
              <span>SEVERITY</span>
              <strong>
                {result.analysis?.severity || "LOW"}
              </strong>
            </div>
          </div>

          {bflaThreats.length > 0 && (
            <div className="threat-result">
              <div className="threat-result-icon">
                <ShieldAlert size={20} />
              </div>

              <div>
                <strong>{bflaThreats[0].type}</strong>
                <p>{bflaThreats[0].reason}</p>
              </div>

              <span className="threat-severity">
                {bflaThreats[0].severity}
              </span>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default BFLADetection;