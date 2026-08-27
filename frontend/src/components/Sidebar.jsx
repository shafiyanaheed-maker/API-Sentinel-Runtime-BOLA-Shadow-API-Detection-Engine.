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
      { label: "Dashboard", icon: LayoutDashboard, active: true },
      { label: "API Monitor", icon: Activity },
    ],
  },
  {
    section: "DETECTION",
    items: [
      { label: "BOLA Detection", icon: LockKeyhole },
      { label: "BFLA Detection", icon: ShieldCheck },
      { label: "Shadow APIs", icon: Box },
      { label: "Threat Center", icon: AlertTriangle },
    ],
  },
];

function Sidebar() {
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

              return (
                <a
                  href="#"
                  key={item.label}
                  className={`nav-link ${item.active ? "active" : ""}`}
                >
                  <Icon size={18} strokeWidth={1.9} />
                  <span>{item.label}</span>

                  {item.active && (
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
        <div className="quick-action">
          <div className="quick-action-icon">
            <Zap size={16} />
          </div>

          <div>
            <strong>Quick Scan</strong>
            <span>Analyze an API request</span>
          </div>

          <ChevronRight size={15} />
        </div>

        <div className="bottom-links">
          <a href="#" className="bottom-link">
            <Terminal size={17} />
            <span>Developer Tools</span>
          </a>

          <a href="#" className="bottom-link">
            <Settings size={17} />
            <span>Settings</span>
          </a>

          <a href="#" className="bottom-link">
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