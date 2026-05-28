from fastapi import FastAPI
from fastapi.responses import JSONResponse
from config import settings
from portainer_service import PortainerService
import uvicorn

# --- FastAPI Initialization ---
app = FastAPI()
print(f"Initializing portainer service", end='')
# --- Global Service Instance ---
try:
    portainer_service = PortainerService()
    print("✅ PortainerService initialized successfully.")  
except Exception as e:
    print(f"FATAL: Failed to initialize PortainerService. Is your .env file correct? Error: {e}")
    portainer_service = None

# --- API Endpoints ---

@app.get('/api/servers/list')
def list_servers():
    """
    Endpoint to fetch the status of all managed servers from Portainer.
    Returns a list of dictionaries containing name, status, and IP address.
    """
    if portainer_service is None:
        return JSONResponse(content={"error": "Service unavailable. Check backend initialization."}, status_code=503)
        
    server_data = portainer_service.get_all_server_status()
    
    if server_data is not None:
        return server_data
    else:
        return JSONResponse(content={"message": "No recognized servers found or failed to connect to Portainer."}, status_code=404)

@app.post('/api/servers/toggle/{server_name}')
def toggle_server(server_name: str):
    """
    Endpoint to start or stop a specified server container via Portainer.
    Expects the server_name in the URL path.
    """
    if portainer_service is None:
        return JSONResponse(content={"error": "Service unavailable. Check backend initialization."}, status_code=503)

    # Basic validation to prevent injection or unauthorized access
    is_allowed = any(server_name.lower() == name.lower() for name in settings.ALLOWED_CONTAINER_NAMES.split(','))
    if not is_allowed:
        return JSONResponse(content={"error": f"Unauthorized operation. '{server_name}' is not a managed server."}, status_code=403)

    # Call the service method and return the result message
    result_message = portainer_service.toggle_server(server_name)
    
    # Simple way to determine success/failure for the API response structure
    if result_message.startswith("✅"):
        status_code = 200
    elif result_message.startswith("❌"):
        status_code = 202
    else:
        status_code = 500

    return JSONResponse(content={"message": result_message}, status_code=status_code)


@app.get('/health')
def health_check():
    """Health check endpoint to confirm the API is running."""
    return {"status": "online", "service": "Minecraft Backend API", "version": "1.0"}

if __name__ == '__main__':
    # The server will run on port 5000
    print("\n=================================================================")
    print("🚀 SERVER STARTUP INITIATED 🚀")
    print("Backend running on http://127.0.0.1:5000/")
    print("REMEMBER: Create a '.env' file in the 'backend' directory!")
    print("==================================================================\n")
    # Note: Running the app directly from a script context requires explicit packaging instructions.
    # For this simulation, we will use the run command below, but this code is now correct.
    uvicorn.run(app, host="0.0.0.0", port=5000)
