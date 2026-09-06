import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  FileWarning,
  LockKeyhole,
  ShieldAlert,
  ShieldCheck,
  Users,
  Zap,
} from "lucide-react";

import "./OWASPSecurity.css";

const owaspCategories = [
  {
    id: "API1",
    title: "Broken Object Level Authorization",
    shortTitle: "BOLA",
    description:
      "Attackers access objects belonging to another user by manipulating object identifiers.",
    severity: "HIGH",
    icon: LockKeyhole,
    status: "Detected",
    detection: "Runtime BOLA detection",
  },
  {
    id: "API2",
    title: "Broken Authentication",
    shortTitle: "Authentication",
    description:
      "Weak authentication controls can allow attackers to impersonate users or access protected APIs.",
    severity: "MEDIUM",
    icon: ShieldAlert,
    status: "Monitoring",
    detection: "Authentication monitoring",
  },
  {
    id: "API3",
    title: "Broken Object Property Level Authorization",
    shortTitle: "Property Authorization",
    description:
      "Sensitive object properties may be exposed or modified without appropriate authorization.",
    severity: "LOW",
    icon: FileWarning,
    status: "Monitoring",
    detection: "Property-level review",
  },
  {
    id: "API4",
    title: "Unrestricted Resource Consumption",
    shortTitle: "Rate Limiting",
    description:
      "Excessive requests can consume application resources and enable denial-of-service attacks.",
    severity: "HIGH",
    icon: Zap,
    status: "Protected",
    detection: "Rate-limit enforcement",
  },
  {
    id: "API5",
    title: "Broken Function Level Authorization",
    shortTitle: "BFLA",
    description:
      "Users may invoke administrative or privileged functions without sufficient authorization.",
    severity: "HIGH",
    icon: Users,
    status: "Detected",
    detection: "Runtime BFLA detection",
  },
  {
    id: "API6",
    title: "Unrestricted Access to Sensitive Business Flows",
    shortTitle: "Business Flows",
    description:
      "Critical business operations can be abused when automated access is not properly controlled.",
    severity: "MEDIUM",
    icon: CircleAlert,
    status: "Monitoring",
    detection: "Business-flow controls",
  },
  {
    id: "API7",
    title: "Server Side Request Forgery",
    shortTitle: "SSRF",
    description:
      "Server-side request functionality can be abused to access unintended internal resources.",
    severity: "LOW",
    icon: AlertTriangle,
    status: "Monitoring",
    detection: "Runtime monitoring",
  },
  {
    id: "API8",
    title: "Security Misconfiguration",
    shortTitle: "Misconfiguration",
    description:
      "Insecure API configuration can expose unnecessary services, methods, headers, or information.",
    severity: "MEDIUM",
    icon: SettingsIcon,
    status: "Monitoring",
    detection: "Security configuration review",
  },
  {
    id: "API9",
    title: "Improper Inventory Management",
    shortTitle: "Shadow APIs",
    description:
      "Undocumented, deprecated, or forgotten API endpoints increase the attack surface.",
    severity: "HIGH",
    icon: FileWarning,
    status: "Detected",
    detection: "Shadow/Zombie API discovery",
  },
  {
    id: "API10",
    title: "Unsafe Consumption of APIs",
    shortTitle: "Unsafe Consumption",
    description:
      "Untrusted third-party API responses can introduce security risks into dependent systems.",
    severity: "LOW",
    icon: ShieldCheck,
    status: "Monitoring",
    detection: "API dependency monitoring",
  },
];

function SettingsIcon(props) {
  return <ShieldCheck {...props} />;
}

function getSeverityClass(severity) {
  return severity.toLowerCase();
}

function OWASPSecurity() {
  const detectedCount = owaspCategories.filter(
    (item) => item.status === "Detected"
  ).length;

  const protectedCount = owaspCategories.filter(
    (item) => item.status === "Protected"
  ).length;

  const monitoringCount = owaspCategories.filter(
    (item) => item.status === "Monitoring"
  ).length;

  const highSeverityCount = owaspCategories.filter(
    (item) => item.severity === "HIGH"
  ).length;

  return (
    <div className="owasp-page">
      <header className="owasp-header">
        <div className="owasp-heading">
          <div className="owasp-heading-icon">
            <ShieldCheck size={24} />
          </div>

          <div>
            <div className="owasp-eyebrow">
              SECURITY POSTURE
            </div>

            <h1>OWASP API Security</h1>

            <p>
              Runtime vulnerability coverage mapped to the
              OWASP API Security Top 10.
            </p>
          </div>
        </div>

        <div className="owasp-live-status">
          <span className="owasp-live-dot" />
          Runtime monitoring active
        </div>
      </header>

      <section className="owasp-summary-grid">
        <div className="owasp-summary-card">
          <div className="owasp-summary-top">
            <span>OWASP CATEGORIES</span>
            <ShieldCheck size={17} />
          </div>

          <strong>10</strong>

          <p>API Security Top 10 categories mapped</p>
        </div>

        <div className="owasp-summary-card">
          <div className="owasp-summary-top">
            <span>DETECTIONS</span>
            <AlertTriangle size={17} />
          </div>

          <strong>{detectedCount}</strong>

          <p>Categories currently producing findings</p>
        </div>

        <div className="owasp-summary-card">
          <div className="owasp-summary-top">
            <span>PROTECTED</span>
            <CheckCircle2 size={17} />
          </div>

          <strong>{protectedCount}</strong>

          <p>Categories covered by active controls</p>
        </div>

        <div className="owasp-summary-card">
          <div className="owasp-summary-top">
            <span>HIGH RISK</span>
            <ShieldAlert size={17} />
          </div>

          <strong>{highSeverityCount}</strong>

          <p>Categories carrying high severity coverage</p>
        </div>
      </section>

      <section className="owasp-posture">
        <div className="owasp-posture-header">
          <div>
            <h2>Security Coverage</h2>
            <p>
              Current runtime coverage across the OWASP API
              Security Top 10.
            </p>
          </div>

          <div className="owasp-posture-count">
            <strong>{monitoringCount}</strong>
            <span>under monitoring</span>
          </div>
        </div>

        <div className="owasp-progress">
          <div
            className="owasp-progress-fill"
            style={{
              width: `${((detectedCount + protectedCount) /
                owaspCategories.length) *
                100}%`,
            }}
          />
        </div>

        <div className="owasp-progress-meta">
          <span>
            Active detection/control coverage
          </span>

          <strong>
            {Math.round(
              ((detectedCount + protectedCount) /
                owaspCategories.length) *
                100
            )}
            %
          </strong>
        </div>
      </section>

      <section className="owasp-panel">
        <div className="owasp-panel-header">
          <div>
            <div className="owasp-panel-title-row">
              <FileWarning size={18} />
              <h2>OWASP API Security Top 10</h2>
            </div>

            <p>
              Vulnerability categories connected to API-Sentinel
              runtime security controls.
            </p>
          </div>
        </div>

        <div className="owasp-category-list">
          {owaspCategories.map((item) => {
            const Icon = item.icon;

            return (
              <article
                className="owasp-category"
                key={item.id}
              >
                <div className="owasp-category-number">
                  {item.id}
                </div>

                <div className="owasp-category-icon">
                  <Icon size={19} />
                </div>

                <div className="owasp-category-content">
                  <div className="owasp-category-title">
                    <h3>{item.title}</h3>

                    <span
                      className={`owasp-severity ${getSeverityClass(
                        item.severity
                      )}`}
                    >
                      {item.severity}
                    </span>
                  </div>

                  <p>{item.description}</p>

                  <div className="owasp-category-meta">
                    <span>
                      Detection:
                      <strong>{item.detection}</strong>
                    </span>
                  </div>
                </div>

                <div
                  className={`owasp-status ${item.status
                    .toLowerCase()
                    .replace(" ", "-")}`}
                >
                  {item.status === "Detected" && (
                    <AlertTriangle size={13} />
                  )}

                  {item.status === "Protected" && (
                    <CheckCircle2 size={13} />
                  )}

                  {item.status === "Monitoring" && (
                    <ShieldCheck size={13} />
                  )}

                  {item.status}
                </div>

                <ChevronRight
                  className="owasp-category-arrow"
                  size={17}
                />
              </article>
            );
          })}
        </div>
      </section>

      <section className="owasp-footer-card">
        <div className="owasp-footer-icon">
          <ShieldCheck size={20} />
        </div>

        <div>
          <strong>Runtime security posture</strong>

          <p>
            API-Sentinel continuously connects observed API
            behavior with authorization, rate-limit, inventory,
            and security controls to surface OWASP-aligned
            risks.
          </p>
        </div>
      </section>
    </div>
  );
}

export default OWASPSecurity;