import requests
from config import settings

class PortainerService:
    """
    Handles all communication with the external Portainer API
    to manage Minecraft server containers.
    """
    def __init__(self):
        self.api_url = settings.PORTAINER_API_URL
        self.endpoint_ids = [eid.strip() for eid in settings.ENDPOINT_ID.split(',') if eid.strip()]
        self.endpoint_resource = settings.ENDPOINT_RESOURCE
        self.api_key = settings.PORTAINER_API_KEY
        print(f"Initializing PORTAINER SERVICE with endpoints: {self.endpoint_ids}")
        self.allowed_names = [name.strip() for name in settings.ALLOWED_CONTAINER_NAMES.split(',') if name.strip()]
        print(f"Allowed names: {self.allowed_names}")
        self.headers = {
            "X-API-Key": f"{self.api_key}",
            "Content-Type": "application/json"
        }
        print("PortainerService initialized with allowed servers:", self.allowed_names)

    def _make_api_request(self, endpoint_id: str, endpoint: str, method: str = "GET", data: dict = None) -> dict | None:
        """Helper method to safely make requests to the Portainer API."""
        url = f"{self.api_url}/api/endpoints/{endpoint_id}/{self.endpoint_resource}/containers/{endpoint}"
        # Quiet polling requests, log only mutations (POST/DELETE) or errors
        if method != "GET":
            print(f"[MUTATION API] Sending request...")
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params={"all": "true"})
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            # elif method == "DELETE":
            #     response = requests.delete(url, headers=self.headers, params=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            # Handle successful mutations that return empty bodies (202/204)
            if response.status_code in (200, 202, 204):
                if response.status_code == 200:
                    return response.json()
                return True  # or None, depending on your convention

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
        filtered_servers = []
        for endpoint_id in self.endpoint_ids:
            all_containers = self._make_api_request(endpoint_id=endpoint_id, endpoint="json", method="GET")
            
            if not all_containers or not isinstance(all_containers, list):
                continue

            # Filter and format the list to only include allowed servers
            for container in all_containers:
                # Get container name (first element of Names list, remove leading /)
                names = container.get('Names', [])
                container_name = names[0].lstrip('/') if names else None
                if container_name and container_name in self.allowed_names:
                    state = container.get('State', '').lower()
                    status = container.get('Status', 'UNKNOWN')
                    list_port = container.get('Ports','')
                    if list_port:
                        port = list_port[0]['PublicPort']
                    else:
                        port = ''
                    
                    if state == 'running' or 'running' in state or 'up' in status.lower() or 'running' in status.lower():
                        clean_status = 'running'
                    else:
                        clean_status = 'stopped'
                        
                    # IPAddress is nested inside NetworkSettings.Networks.bridge
                    network = container.get('NetworkSettings', {}).get('Networks', {})
                    ip_address = '10.0.0.11' if endpoint_id=='49' else '10.0.0.250'
                    
                    filtered_servers.append({
                        "id": container.get('Id', 'N/A'),
                        "name": container_name,
                        "status": clean_status,
                        "ip_address": ip_address,
                        "port": port,
                        "endpoint_id": endpoint_id
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
        container_id = server_data.get('id')
        if not container_id:
            return f"Error: Could not determine container ID for '{server_name}'."
        if not server_data:
            return f"Error: Server '{server_name}' not found in Portainer list."

        current_status = server_data['status']
        endpoint_id = server_data.get('endpoint_id')
        if not endpoint_id:
            return f"Error: Could not determine endpoint ID for '{server_name}'."
        
        if 'running' in current_status.lower():
            # Attempt to stop the container
            
            stop_response = self._make_api_request(endpoint_id=endpoint_id, endpoint=f"{container_id}/stop", method="POST")
            if stop_response:
                return f"✅ Successfully sent stop command to {server_name}. It should now be stopping."
            else:
                return f"❌ Failed to send stop command to {server_name}. Check logs."

        elif 'stopped' in current_status.lower():
            # Attempt to start the container
            print(f"Attempting to START server: {server_name} on endpoint {endpoint_id}...")
            start_response = self._make_api_request(endpoint_id=endpoint_id, endpoint=f"{container_id}/start", method="POST")
            if start_response:
                return f"✅ Successfully sent start command to {server_name}. It should now be running."
            else:
                return f"❌ Failed to send start command to {server_name}. Check logs."
        else:
            return f"⚠️ Warning: Server '{server_name}' is in an unknown state: '{current_status}'. Manual check required."
