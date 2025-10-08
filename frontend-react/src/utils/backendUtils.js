// Utility to check backend health and attempt to start it
export const checkBackendHealth = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch('http://localhost:8000/status', {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

export const startBackendIfNeeded = async () => {
  const isHealthy = await checkBackendHealth();
  
  if (!isHealthy) {
    console.log('Backend not responding, attempting to start...');
    
    // For development, we can show instructions to user
    return {
      needsManualStart: true,
      instructions: [
        'Backend server is not running. Please start it manually:',
        '1. Open a terminal in the backend directory',
        '2. Run: C:/Users/shrin/OneDrive/Desktop/CAG/.venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000',
        'OR',
        'Run the start-app.bat file in the project root directory'
      ]
    };
  }
  
  return { needsManualStart: false };
};

export const waitForBackend = async (maxRetries = 30, delay = 10000) => {
  for (let i = 0; i < maxRetries; i++) {
    const isHealthy = await checkBackendHealth();
    if (isHealthy) {
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  return false;
};
