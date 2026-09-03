const API_BASE_URL = "http://127.0.0.1:8000";

async function analyzeRequest({
  method,
  path,
  authenticated_user_id,
  user_role,
  client_id = "dashboard-client",
}) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      method,
      path,
      authenticated_user_id,
      user_role,
      client_id,
    }),
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json();
}

async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return response.json();
}

export { analyzeRequest, checkHealth };