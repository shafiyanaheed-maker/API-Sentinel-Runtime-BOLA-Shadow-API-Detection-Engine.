import { useEffect, useState } from "react";

import "./App.css";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import FeaturePage from "./pages/FeaturePage";
import Landing from "./pages/Landing";

function getCurrentPath() {
  const path = window.location.pathname;

  if (path === "/" || path === "") {
    return "/";
  }

  return path;
}

function App() {
  const [currentPath, setCurrentPath] = useState(getCurrentPath);

  useEffect(() => {
    function handlePopState() {
      setCurrentPath(getCurrentPath());
    }

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  function navigate(path) {
    if (path === currentPath) {
      return;
    }

    window.history.pushState({}, "", path);
    setCurrentPath(path);
  }

  function handleGetStarted() {
    navigate("/dashboard");
  }

  if (currentPath === "/") {
    return <Landing onGetStarted={handleGetStarted} />;
  }

  return (
    <Layout
      currentPath={currentPath}
      onNavigate={navigate}
    >
      {currentPath === "/dashboard" ? (
        <Dashboard />
      ) : (
        <FeaturePage path={currentPath} />
      )}
    </Layout>
  );
}

export default App;