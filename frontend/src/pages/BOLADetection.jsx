import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  LockKeyhole,
  ShieldAlert,
} from "lucide-react";

import { analyzeRequest } from "../services/api";
import "./SecurityPages.css";

function saveThreat(result) {
  const threats = result?.analysis?.threats || [];

  if (threats.length === 0) {
    return;
  }

  const existing = JSON.parse(
    localStorage.getItem("apiSentinelThreats") || "[]"
  );

  const newThreats = threats.map((threat) => ({
    ...threat,
    endpoint: result.request?.path || "/users/105",
    detectedAt: new Date().toISOString(),
    status: "Blocked",
  }));

  localStorage.setItem(
    "apiSentinelThreats",
    JSON.stringify([...newThreats, ...existing].slice(0, 50))
  );
}

function BOLADetection() {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/users/105");
  const [userId, setUserId] = useState("102");
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
        authenticated_user_id: Number(userId),
        user_role: "user",
        client_id: "bola-detection-page",
      });

      setResult(response);
      saveThreat({
        ...response,
        request: {
          method,
          path,
        },
      });
    } catch (scanError) {
      console.error("BOLA scan failed:", scanError);
      setError(
        "Unable to connect to the API-Sentinel backend. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const threats = result?.analysis?.threats || [];
  const bolaThreats = threats.filter(
    (threat) => threat.type === "BOLA"
  );

  return (
    <div className="security-page">
      <header className="security-page-header">
        <div>
          <div className="security-page-title-row">
            <div className="security-page-icon bola-icon">
              <LockKeyhole size={23} />
            </div>

            <div>
              <h1>BOLA Detection</h1>
              <p>
                Detect unauthorized object-level API access in
                real time.
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
          <strong>BOLA</strong>
          <p>Broken Object Level Authorization</p>
        </div>

        <div className="security-info-card">
          <span className="security-info-label">SEVERITY</span>
          <strong className="severity-high">HIGH</strong>
          <p>Unauthorized object access</p>
        </div>

        <div className="security-info-card">
          <span className="security-info-label">ENGINE</span>
          <strong>Runtime</strong>
          <p>Analyzed by API-Sentinel</p>
        </div>
      </section>

      <section className="security-panel">
        <div className="security-panel-header">
          <div>
            <h2>Test Object Access</h2>
            <p>
              Send a request through the runtime BOLA detection
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
              API Path
              <input
                value={path}
                onChange={(event) =>
                  setPath(event.target.value)
                }
                placeholder="/users/105"
              />
            </label>

            <label>
              Authenticated User ID
              <input
                type="number"
                value={userId}
                onChange={(event) =>
                  setUserId(event.target.value)
                }
                min="1"
              />
            </label>
          </div>

          <div className="security-form-actions">
            <span className="security-hint">
              Try user <strong>102</strong> accessing{" "}
              <strong>/users/105</strong> to demonstrate BOLA.
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

            {bolaThreats.length > 0 ? (
              <div className="result-badge danger">
                <AlertTriangle size={15} />
                BOLA Detected
              </div>
            ) : (
              <div className="result-badge safe">
                <CheckCircle2 size={15} />
                No BOLA Detected
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
              <span>USER ID</span>
              <strong>{userId}</strong>
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

          {bolaThreats.length > 0 && (
            <div className="threat-result">
              <div className="threat-result-icon">
                <ShieldAlert size={20} />
              </div>

              <div>
                <strong>{bolaThreats[0].type}</strong>
                <p>{bolaThreats[0].reason}</p>
              </div>

              <span className="threat-severity">
                {bolaThreats[0].severity}
              </span>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default BOLADetection;