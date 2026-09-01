import { useEffect, useState } from "react";

import "./App.css";
import "./theme.css";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";
import ThemeToggle from "./components/ThemeToggle";

function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [theme, setTheme] = useState(
    () => localStorage.getItem("api-sentinel-theme") || "dark"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("api-sentinel-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((currentTheme) =>
      currentTheme === "dark" ? "light" : "dark"
    );
  };

  if (!showDashboard) {
    return (
      <>
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
        <Landing
          onGetStarted={() => setShowDashboard(true)}
        />
      </>
    );
  }

  return (
    <>
      <ThemeToggle theme={theme} onToggle={toggleTheme} />
      <Layout>
        <Dashboard />
      </Layout>
    </>
  );
}

export default App;
