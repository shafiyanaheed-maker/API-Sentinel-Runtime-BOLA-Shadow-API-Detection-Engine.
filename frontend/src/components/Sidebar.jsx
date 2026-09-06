import {
  Activity,
  AlertTriangle,
  Box,
  ChevronRight,
  CircleHelp,
  FileWarning,
  LayoutDashboard,
  LockKeyhole,
  Settings,
  ShieldCheck,
  Terminal,
  Zap,
} from "lucide-react";

const navigation = [
  {
    section: "OVERVIEW",
    items: [
      {
        label: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard",
      },
      {
        label: "API Monitor",
        icon: Activity,
        path: "/api-monitor",
      },
    ],
  },
  {
    section: "DETECTION",
    items: [
      {
        label: "BOLA Detection",
        icon: LockKeyhole,
        path: "/bola-detection",
      },
      {
        label: "BFLA Detection",
        icon: ShieldCheck,
        path: "/bfla-detection",
      },
      {
        label: "Shadow APIs",
        icon: Box,
        path: "/shadow-apis",
      },
      {
        label: "Threat Center",
        icon: AlertTriangle,
        path: "/threat-center",
      },
    ],
  },
];

function Sidebar({ currentPath, onNavigate }) {
  function handleNavigation(event, path) {
    event.preventDefault();
    onNavigate(path);
  }

  function isActive(path) {
    return currentPath === path;
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <ShieldCheck size={21} strokeWidth={2.2} />
        </div>

        <div className="brand-text">
          <div className="brand-name">
            API<span>-</span>Sentinel
          </div>

          <div className="brand-subtitle">RUNTIME SECURITY</div>
        </div>
      </div>

      <div className="environment">
        <span className="environment-dot" />
        <span>PROTECTION ACTIVE</span>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((group) => (
          <div className="nav-group" key={group.section}>
            <div className="nav-section-title">{group.section}</div>

            {group.items.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);

              return (
                <a
                  href={item.path}
                  key={item.label}
                  className={`nav-link ${active ? "active" : ""}`}
                  onClick={(event) => handleNavigation(event, item.path)}
                >
                  <Icon size={18} strokeWidth={1.9} />

                  <span>{item.label}</span>

                  {active && (
                    <ChevronRight
                      className="nav-arrow"
                      size={15}
                      strokeWidth={2}
                    />
                  )}
                </a>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <a
          href="/quick-scan"
          className="quick-action"
          onClick={(event) => handleNavigation(event, "/quick-scan")}
        >
          <div className="quick-action-icon">
            <Zap size={16} />
          </div>

          <div>
            <strong>Quick Scan</strong>
            <span>Analyze an API request</span>
          </div>

          <ChevronRight size={15} />
        </a>

        <div className="bottom-links">
          <a
            href="/developer-tools"
            className={`bottom-link ${
              isActive("/developer-tools") ? "active" : ""
            }`}
            onClick={(event) =>
              handleNavigation(event, "/developer-tools")
            }
          >
            <Terminal size={17} />
            <span>Developer Tools</span>
          </a>

          <a
            href="/settings"
            className={`bottom-link ${
              isActive("/settings") ? "active" : ""
            }`}
            onClick={(event) => handleNavigation(event, "/settings")}
          >
            <Settings size={17} />
            <span>Settings</span>
          </a>

          <a
            href="/help"
            className={`bottom-link ${
              isActive("/help") ? "active" : ""
            }`}
            onClick={(event) => handleNavigation(event, "/help")}
          >
            <CircleHelp size={17} />
            <span>Help & Docs</span>
          </a>
        </div>

        <div className="sidebar-footer">
          <div className="footer-status">
            <span className="online-dot" />
            All systems operational
          </div>

          <span className="version">v0.1.0</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;