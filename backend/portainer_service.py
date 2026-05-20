import requests
from typing import List
from flask_app.config import settings

class PortainerService:
    """
    Handles all communication with the external Portainer API
    to manage Minecraft server containers.
    """
    def __init__(self):
        self.base_url = settings.PORTAINER_API_URL
        self.api_key = settings.PORTAINER_API_KEY
        self.allowed_names = [name.strip() for name in settings.ALLOWED_CONTAINER_NAMES.split(',') if name.strip()]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        print("PortainerService initialized with allowed servers:", self.allowed_names)

    def _make_api_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict | None:
        """Helper method to safely make requests to the Portainer API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"🚨 Portainer API Error ({e.response.status_code}): Could not reach Portainer or container status is incorrect. Details: {e.response.text[:100]}...")
            return None
        except requests.exceptions.ConnectionError:
            print("🚨 Connection Error: Could not connect to Portainer. Check URL and API Key.")
            return None
        except Exception as e:
            print(f"🚨 An unexpected error occurred during Portainer communication: {e}")
            return None

    def get_all_server_status(self) -> list[dict]:
        """
        Fetches the status of all monitored containers from Portainer.
        Only returns containers matching allowed names.
        """
        all_containers = self._make_api_request(endpoint="container/list", method="GET")
        if not all_containers or not isinstance(all_containers, list):
            return []

        # Filter and format the list to only include allowed servers
        filtered_servers = []
        for container in all_containers:
            container_name = container.get('Name')
            if container_name and container_name in self.allowed_names:
                status = container.get('Status', 'UNKNOWN')
                ip_address = container.get('IPAddress', 'N/A')
                filtered_servers.append({
                    "name": container_name,
                    "status": status,
                    "ip_address": ip_address
                })
        return filtered_servers

    def toggle_server(self, server_name: str) -> str:
        """
        Toggles the state of a specified server container (Start/Stop).
        """
        if server_name not in self.allowed_names:
            return f"Error: '{server_name}' is not a recognized server name."

        # 1. Check current status first
        current_servers = self.get_all_server_status()
        server_data = next((s for s in current_servers if s['name'] == server_name), None)

        if not server_data:
            return f"Error: Server '{server_name}' not found in Portainer list."

        current_status = server_data['status']
        
        if 'running' in current_status.lower():
            # Attempt to stop the container
            print(f"Attempting to STOP server: {server_name}...")
            stop_response = self._make_api_request(endpoint=f"container/stop/{server_name}", method="POST")
            if stop_response:
                return f"✅ Successfully sent stop command to {server_name}. It should now be stopping."
            else:
                return f"❌ Failed to send stop command to {server_name}. Check logs."

        elif 'stopped' in current_status.lower():
            # Attempt to start the container
            print(f"Attempting to START server: {server_name}...")
            start_response = self._make_api_request(endpoint=f"container/start/{server_name}", method="POST")
            if start_response:
                return f"✅ Successfully sent start command to {server_name}. It should now be running."
            else:
                return f"❌ Failed to send start command to {server_name}. Check logs."
        else:
            return f"⚠️ Warning: Server '{server_name}' is in an unknown state: '{current_status}'. Manual check required."