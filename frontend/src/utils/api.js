const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'; // Fallback added

// RENAME THIS FUNCTION
export async function executeAgentCommand(command) {
  try {
    // The endpoint is /api/execute-agent, not /api/agents/execute
    const response = await fetch(`${API_URL}/api/execute-agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error executing command:", error);
    // Re-throw the error so the component can catch it and show a message
    throw error;
  }
}