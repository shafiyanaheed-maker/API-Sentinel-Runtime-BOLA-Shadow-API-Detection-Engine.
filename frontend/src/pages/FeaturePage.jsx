import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Box,
  CircleHelp,
  Code2,
  FileWarning,
  LockKeyhole,
  Settings,
  ShieldCheck,
  Zap,
} from "lucide-react";

import { checkHealth } from "../services/api";

const PAGE_CONFIG = {
  "/api-monitor": {
    title: "API Monitor",
    subtitle: "Monitor incoming API traffic and runtime activity.",
    icon: Activity,
    status: "Traffic monitoring active",
    description:
      "API-Sentinel continuously monitors API requests and prepares them for runtime security analysis.",
    sections: [
      ["Requests monitored", "1", "Requests currently analyzed by the runtime engine."],
      ["Active endpoints", "1", "Endpoints observed during runtime monitoring."],
      ["Protected endpoints", "1", "Endpoints currently covered by security checks."],
    ],
  },

  "/bola-detection": {
    title: "BOLA Detection",
    subtitle: "Monitor object-level authorization attacks.",
    icon: LockKeyhole,
    status: "Object authorization protection active",
    description:
      "BOLA detection identifies attempts where an authenticated user accesses an object belonging to another user.",
    sections: [
      ["Detection engine", "Active", "Runtime BOLA detection is enabled."],
      ["Threat level", "High", "Cross-user object access is treated as a high-severity threat."],
      ["Protected objects", "3", "Mock ownership rules are currently available to the detector."],
    ],
  },

  "/bfla-detection": {
    title: "BFLA Detection",
    subtitle: "Monitor function-level authorization attacks.",
    icon: ShieldCheck,
    status: "Function authorization protection active",
    description:
      "BFLA detection checks whether a user's role is authorized to access protected functions and endpoints.",
    sections: [
      ["Detection engine", "Active", "Runtime BFLA role checks are enabled."],
      ["Authorization model", "Role based", "Endpoint access is evaluated against user roles."],
      ["Default policy", "Deny", "Unauthorized function access is blocked."],
    ],
  },

  "/shadow-apis": {
    title: "Shadow APIs",
    subtitle: "Discover undocumented and untracked API endpoints.",
    icon: Box,
    status: "API discovery module ready",
    description:
      "Shadow API monitoring compares observed API traffic with known API definitions to identify undocumented endpoints.",
    sections: [
      ["Discovery status", "Ready", "The Shadow API monitoring area is ready for traffic data."],
      ["Known APIs", "0", "Officially documented endpoints currently available to this view."],
      ["Shadow APIs", "0", "Undocumented endpoints currently detected."],
    ],
  },

  "/threat-center": {
    title: "Threat Center",
    subtitle: "Review runtime API security threats and enforcement events.",
    icon: AlertTriangle,
    status: "Threat monitoring active",
    description:
      "The Threat Center provides a central location for reviewing detected BOLA, BFLA, rate-limit, and enforcement events.",
    sections: [
      ["Open threats", "0", "Threats currently requiring investigation."],
      ["Blocked events", "2", "Security events currently represented in the dashboard."],
      ["Monitoring", "Active", "Runtime security monitoring is operational."],
    ],
  },

  "/quick-scan": {
    title: "Quick Scan",
    subtitle: "Analyze an API request against API-Sentinel security checks.",
    icon: Zap,
    status: "Runtime scanner ready",
    description:
      "Quick Scan provides a direct interface for testing an API request against the runtime security engine.",
    sections: [
      ["BOLA check", "Ready", "Object-level authorization can be evaluated."],
      ["BFLA check", "Ready", "Function-level authorization can be evaluated."],
      ["Rate limiting", "Ready", "Request volume can be evaluated."],
    ],
  },

  "/developer-tools": {
    title: "Developer Tools",
    subtitle: "Inspect and test API-Sentinel runtime security behavior.",
    icon: Code2,
    status: "Developer tools ready",
    description:
      "Developer tools provide a workspace for testing API requests and inspecting security decisions during development.",
    sections: [
      ["Runtime analyzer", "Available", "The runtime analyzer is connected to the backend."],
      ["API endpoint", "/api/analyze", "Requests can be sent to the runtime analysis API."],
      ["Health endpoint", "/api/health", "Backend health can be checked from the frontend."],
    ],
  },

  "/settings": {
    title: "Settings",
    subtitle: "Configure API-Sentinel security and monitoring settings.",
    icon: Settings,
    status: "Configuration ready",
    description:
      "This area will contain runtime security configuration such as monitoring and enforcement settings.",
    sections: [
      ["Protection", "Active", "API-Sentinel protection is enabled."],
      ["Rate limiting", "Enabled", "Runtime request-rate protection is available."],
      ["Authorization", "Enabled", "BOLA and BFLA authorization checks are available."],
    ],
  },

  "/help": {
    title: "Help & Docs",
    subtitle: "Learn how API-Sentinel security monitoring works.",
    icon: CircleHelp,
    status: "Documentation available",
    description:
      "Use this section to understand the security modules, runtime analysis flow, and dashboard controls.",
    sections: [
      ["BOLA", "Object level", "Protects access to resources belonging to other users."],
      ["BFLA", "Function level", "Protects privileged API functions from unauthorized roles."],
      ["Shadow APIs", "Discovery", "Identifies API endpoints that are not officially documented."],
    ],
  },
};

function FeaturePage({ path }) {
  const [backendStatus, setBackendStatus] = useState("Checking");

  const config = PAGE_CONFIG[path] || PAGE_CONFIG["/api-monitor"];
  const Icon = config.icon;

  useEffect(() => {
    let isMounted = true;

    async function loadHealth() {
      try {
        await checkHealth();

        if (isMounted) {
          setBackendStatus("Online");
        }
      } catch {
        if (isMounted) {
          setBackendStatus("Offline");
        }
      }
    }

    loadHealth();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard feature-page">
      <header className="dashboard-header">
        <div>
          <h1>{config.title}</h1>
          <p>{config.subtitle}</p>
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

      <section className="feature-hero-card">
        <div className="feature-icon">
          <Icon size={24} strokeWidth={1.9} />
        </div>

        <div>
          <div className="feature-status">
            <span className="environment-dot" />
            {config.status}
          </div>

          <h2>{config.title}</h2>

          <p>{config.description}</p>
        </div>
      </section>

      <section className="feature-grid">
        {config.sections.map(([label, value, description]) => (
          <article className="feature-card" key={label}>
            <span className="feature-card-label">{label}</span>
            <strong>{value}</strong>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <section className="feature-information">
        <div className="section-heading">
          <div>
            <h2>Security Module</h2>
            <p>API-Sentinel runtime security capability</p>
          </div>

          <span className="inventory-count">ACTIVE</span>
        </div>

        <div className="feature-information-body">
          <FileWarning size={20} />
          <div>
            <strong>{config.title}</strong>
            <p>
              This module is connected to the API-Sentinel security console and
              is ready to work with runtime security data.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default FeaturePage;