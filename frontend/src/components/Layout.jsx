import Sidebar from "./Sidebar";

function Layout({ children, currentPath, onNavigate }) {
  return (
    <div className="app-shell">
      <Sidebar
        currentPath={currentPath}
        onNavigate={onNavigate}
      />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;