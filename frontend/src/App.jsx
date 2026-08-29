import { useState } from "react";

import "./App.css";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";

function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  if (!showDashboard) {
    return (
      <Landing
        onGetStarted={() => setShowDashboard(true)}
      />
    );
  }

  return (
    <Layout>
      <Dashboard />
    </Layout>
  );
}

export default App;