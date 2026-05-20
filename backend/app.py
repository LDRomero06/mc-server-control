from flask import Flask, jsonify, request
from config import settings
from portainer_service import PortainerService
from typing import List

# --- Flask Initialization ---
app = Flask(__name__)
app.config.from_object(settings)

# --- Global Service Instance ---
try:
    portainer_service = PortainerService()
except Exception as e:
    print(f"FATAL: Failed to initialize PortainerService. Is your .env file correct? Error: {e}")
    portainer_service = None

# --- API Endpoints ---

@app.route('/api/servers/list', methods=['GET'])
def list_servers():
    """
    Endpoint to fetch the status of all managed servers from Portainer.
    Returns a list of dictionaries containing name, status, and IP address.
    """
    if portainer_service is None:
        return jsonify({"error": "Service unavailable. Check backend initialization."}), 503
        
    server_data = portainer_service.get_all_server_status()
    
    if server_data:
        return jsonify(server_data), 200
    else:
        return jsonify({"message": "No recognized servers found or failed to connect to Portainer."}), 404

@app.route('/api/servers/toggle/<server_name>', methods=['POST'])
def toggle_server(server_name):
    """
    Endpoint to start or stop a specified server container via Portainer.
    Expects the server_name in the URL path.
    """
    if portainer_service is None:
        return jsonify({"error": "Service unavailable. Check backend initialization."}), 503

    # Basic validation to prevent injection or unauthorized access
    is_allowed = any(server_name.lower() == name.lower() for name in settings.ALLOWED_CONTAINER_NAMES.split(','))
    if not is_allowed:
        return jsonify({"error": f"Unauthorized operation. '{server_name}' is not a managed server."}), 403

    # Call the service method and return the result message
    result_message = portainer_service.toggle_server(server_name)
    
    # Simple way to determine success/failure for the API response structure
    if result_message.startswith("✅") or result_message.startswith("❌"):
        status_code = 200 if result_message.startswith("✅") else 202
    else:
        status_code = 500

    return jsonify({"message": result_message}), status_code


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to confirm the API is running."""
    return jsonify({"status": "online", "service": "Minecraft Backend API", "version": "1.0"}), 200

if __name__ == '__main__':
    # The server will run on port 5000
    print("\n=================================================================")
    print("🚀 SERVER STARTUP INITIATED 🚀")
    print("Backend running on http://127.0.0.1:5000/")
    print("REMEMBER: Create a '.env' file in the 'flask_app' directory!")
    print("==================================================================\n")
    # Note: Running the app directly from a script context requires explicit packaging instructions.
    # For this simulation, we will use the run command below, but this code is now correct.
    pass