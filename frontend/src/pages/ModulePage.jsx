import {
  Activity,
  AlertTriangle,
  Box,
  CheckCircle2,
  Code2,
  FileSearch,
  Gauge,
  LockKeyhole,
  Search,
  Settings,
  ShieldCheck,
  Terminal,
} from "lucide-react";

import "./ModulePage.css";

const moduleContent = {
  monitor: {
    icon: Activity,
    label: "TRAFFIC MONITORING",
    status: "LIVE MONITORING",
    statusClass: "module-status-blue",
    cards: [
      {
        title: "Requests Observed",
        value: "1",
        description: "Requests currently recorded by the runtime engine.",
        icon: Activity,
      },
      {
        title: "Protected Requests",
        value: "1",
        description: "Requests that passed the active security checks.",
        icon: ShieldCheck,
      },
      {
        title: "Blocked Requests",
        value: "0",
        description: "Requests blocked by enforcement controls.",
        icon: AlertTriangle,
      },
    ],
    sectionTitle: "Runtime API Traffic",
    sectionText:
      "API-Sentinel will display observed API requests and their security decisions here.",
    rows: [
      ["GET", "/users/105", "User request", "Analyzed"],
      ["POST", "/api/orders", "Order request", "Monitoring"],
    ],
  },

  bola: {
    icon: LockKeyhole,
    label: "OBJECT-LEVEL AUTHORIZATION",
    status: "PROTECTION ACTIVE",
    statusClass: "module-status-red",
    cards: [
      {
        title: "BOLA Threats",
        value: "1",
        description: "Object-level authorization violations detected.",
        icon: LockKeyhole,
      },
      {
        title: "High Risk",
        value: "1",
        description: "High-severity BOLA events requiring attention.",
        icon: AlertTriangle,
      },
      {
        title: "Blocked",
        value: "1",
        description: "Unauthorized object access attempts blocked.",
        icon: ShieldCheck,
      },
    ],
    sectionTitle: "BOLA Detection Activity",
    sectionText:
      "The runtime engine checks whether a user is attempting to access another user's object.",
    rows: [
      ["BOLA", "/users/105", "HIGH", "Blocked"],
      ["BOLA", "/orders/1002", "HIGH", "Monitoring"],
    ],
  },

  bfla: {
    icon: ShieldCheck,
    label: "FUNCTION-LEVEL AUTHORIZATION",
    status: "PROTECTION ACTIVE",
    statusClass: "module-status-yellow",
    cards: [
      {
        title: "BFLA Threats",
        value: "1",
        description: "Function-level authorization violations detected.",
        icon: ShieldCheck,
      },
      {
        title: "Admin Endpoints",
        value: "1",
        description: "Protected administrative functions monitored.",
        icon: Settings,
      },
      {
        title: "Blocked",
        value: "1",
        description: "Unauthorized function access attempts blocked.",
        icon: AlertTriangle,
      },
    ],
    sectionTitle: "BFLA Detection Activity",
    sectionText:
      "API-Sentinel compares the requester's role with the authorization required by the endpoint.",
    rows: [
      ["BFLA", "/api/admin/users", "HIGH", "Blocked"],
      ["BFLA", "/api/admin/refund", "HIGH", "Protected"],
    ],
  },

  shadow: {
    icon: Box,
    label: "API DISCOVERY",
    status: "DISCOVERY ACTIVE",
    statusClass: "module-status-purple",
    cards: [
      {
        title: "Shadow APIs",
        value: "0",
        description: "Undocumented API endpoints currently detected.",
        icon: Box,
      },
      {
        title: "Known APIs",
        value: "2",
        description: "Endpoints currently present in the API inventory.",
        icon: FileSearch,
      },
      {
        title: "Discovery",
        value: "Active",
        description: "Runtime traffic is ready for endpoint discovery.",
        icon: Search,
      },
    ],
    sectionTitle: "API Discovery",
    sectionText:
      "Observed traffic can be compared with official API definitions to identify undocumented endpoints.",
    rows: [
      ["GET", "/users/{id}", "Known", "Protected"],
      ["POST", "/api/orders", "Known", "Protected"],
      ["GET", "/api/internal/debug", "Shadow", "Review"],
    ],
  },

  threat: {
    icon: AlertTriangle,
    label: "SECURITY ALERTS",
    status: "ALERT CENTER",
    statusClass: "module-status-red",
    cards: [
      {
        title: "Active Threats",
        value: "2",
        description: "Security events currently visible in the console.",
        icon: AlertTriangle,
      },
      {
        title: "High Severity",
        value: "2",
        description: "High-severity events detected by the runtime engine.",
        icon: AlertTriangle,
      },
      {
        title: "Blocked",
        value: "2",
        description: "Threatening requests prevented by enforcement.",
        icon: ShieldCheck,
      },
    ],
    sectionTitle: "Recent Security Alerts",
    sectionText:
      "Centralized view of security events detected by API-Sentinel.",
    rows: [
      ["BOLA", "/users/105", "HIGH", "Blocked"],
      ["BFLA", "/api/admin/users", "HIGH", "Blocked"],
    ],
  },

  scan: {
    icon: Zap,
    label: "REQUEST ANALYSIS",
    status: "READY",
    statusClass: "module-status-blue",
    cards: [
      {
        title: "Detection Engine",
        value: "Ready",
        description: "BOLA and BFLA runtime analysis is available.",
        icon: ShieldCheck,
      },
      {
        title: "Rate Limiting",
        value: "Active",
        description: "Request volume protection is enabled.",
        icon: Gauge,
      },
      {
        title: "Analysis",
        value: "Live",
        description: "Requests can be analyzed through the backend API.",
        icon: Activity,
      },
    ],
    sectionTitle: "Quick API Scan",
    sectionText:
      "Submit an API request to evaluate it against API-Sentinel runtime security checks.",
    rows: [
      ["GET", "/users/105", "BOLA test", "Ready"],
      ["GET", "/api/admin/users", "BFLA test", "Ready"],
    ],
  },

  developer: {
    icon: Terminal,
    label: "DEVELOPER SECURITY",
    status: "TOOLS READY",
    statusClass: "module-status-blue",
    cards: [
      {
        title: "Runtime Analyzer",
        value: "Ready",
        description: "Analyze requests using the security engine.",
        icon: Code2,
      },
      {
        title: "Detection Tests",
        value: "27",
        description: "Automated backend tests currently passing.",
        icon: CheckCircle2,
      },
      {
        title: "API Health",
        value: "Online",
        description: "FastAPI runtime service is reachable.",
        icon: Activity,
      },
    ],
    sectionTitle: "Developer Security Tools",
    sectionText:
      "Developer utilities will provide testing and debugging workflows for API-Sentinel.",
    rows: [
      ["Analyzer", "Runtime request analysis", "Ready", "Available"],
      ["Health", "Backend health check", "Online", "Available"],
      ["Tests", "Security test suite", "27 passed", "Available"],
    ],
  },

  settings: {
    icon: Settings,
    label: "SYSTEM CONFIGURATION",
    status: "READY",
    statusClass: "module-status-green",
    cards: [
      {
        title: "Protection",
        value: "Active",
        description: "Runtime security protection is enabled.",
        icon: ShieldCheck,
      },
      {
        title: "Rate Limiting",
        value: "Active",
        description: "Request volume controls are configured.",
        icon: Gauge,
      },
      {
        title: "Authorization",
        value: "Active",
        description: "BOLA and BFLA authorization checks are enabled.",
        icon: LockKeyhole,
      },
    ],
    sectionTitle: "Security Configuration",
    sectionText:
      "Security controls and runtime configuration will be managed from this section.",
    rows: [
      ["Authorization", "BOLA", "Enabled", "Protected"],
      ["Authorization", "BFLA", "Enabled", "Protected"],
      ["Rate Limit", "Request volume", "Enabled", "Protected"],
    ],
  },

  help: {
    icon: CircleHelp,
    label: "DOCUMENTATION",
    status: "READY",
    statusClass: "module-status-blue",
    cards: [
      {
        title: "BOLA",
        value: "Object",
        description: "Protects object-level authorization boundaries.",
        icon: LockKeyhole,
      },
      {
        title: "BFLA",
        value: "Function",
        description: "Protects privileged API functions and roles.",
        icon: ShieldCheck,
      },
      {
        title: "Shadow APIs",
        value: "Discovery",
        description: "Finds undocumented endpoints from observed traffic.",
        icon: Box,
      },
    ],
    sectionTitle: "API-Sentinel Documentation",
    sectionText:
      "This area will contain explanations of the detection engine, API security controls, and project workflows.",
    rows: [
      ["BOLA Detection", "Object-level authorization", "Available", "Docs"],
      ["BFLA Detection", "Function-level authorization", "Available", "Docs"],
      ["Shadow APIs", "Undocumented endpoint discovery", "Planned", "Docs"],
    ],
  },
};

function ModulePage({ title, subtitle, type }) {
  const content = moduleContent[type];

  const Icon = content.icon;

  return (
    <div className="module-page">
      <header className="module-header">
        <div>
          <div className="module-title-row">
            <div className="module-title-icon">
              <Icon size={22} strokeWidth={1.9} />
            </div>

            <div>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
          </div>
        </div>

        <div className={`module-status ${content.statusClass}`}>
          <span />
          {content.status}
        </div>
      </header>

      <section className="module-cards">
        {content.cards.map((card) => {
          const CardIcon = card.icon;

          return (
            <div className="module-card" key={card.title}>
              <div className="module-card-icon">
                <CardIcon size={18} />
              </div>

              <div className="module-card-label">{card.title}</div>

              <div className="module-card-value">{card.value}</div>

              <div className="module-card-description">
                {card.description}
              </div>
            </div>
          );
        })}
      </section>

      <section className="module-section">
        <div className="module-section-heading">
          <div>
            <h2>{content.sectionTitle}</h2>
            <p>{content.sectionText}</p>
          </div>

          <div className="module-section-badge">
            <span />
            Monitoring
          </div>
        </div>

        <div className="module-table-wrapper">
          <table className="module-table">
            <thead>
              <tr>
                {content.rows[0].map((_, index) => (
                  <th key={index}>
                    {index === 0
                      ? "TYPE"
                      : index === 1
                        ? "ENDPOINT / RESOURCE"
                        : index === 2
                          ? "STATUS"
                          : "ACTION"}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {content.rows.map((row, rowIndex) => (
                <tr key={`${row[0]}-${row[1]}-${rowIndex}`}>
                  {row.map((value, valueIndex) => (
                    <td
                      key={`${value}-${valueIndex}`}
                      className={
                        valueIndex === 0
                          ? "module-table-primary"
                          : valueIndex === 2
                            ? "module-table-status"
                            : ""
                      }
                    >
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="module-ready">
        <CheckCircle2 size={17} />

        <div>
          <strong>{title} module is active.</strong>

          <p>
            This page is now connected to the API-Sentinel frontend navigation
            and is ready for its backend data integration.
          </p>
        </div>
      </section>
    </div>
  );
}

export default ModulePage;