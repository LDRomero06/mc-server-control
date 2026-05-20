import http.server
import socketserver
import os
import sys

PORT = 3213
BUILD_DIR = "build"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Override to catch paths that don't exist physically
        if not path.startswith(f"/{BUILD_DIR}/"):
            path = f"/{BUILD_DIR}/{path}"
        return path

    def do_GET(self):
        # Check if the requested path maps to a real file first
        # This is the core SPA routing fix.
        if not self.path.startswith("/"):
            self.path = "/"
        
        # Attempt to send the directory index listing (shouldn't happen for SPA)
        if self.path.endswith("/"):
            self.path = self.path[:-1]
            
        # Simulate serving index.html for any path that doesn't match a physical file
        # We need to ensure the path used for the request is /index.html
        
        # 1. Check if the request is specifically for index.html or the root
        if self.path == "" or self.path == "/" or self.path.endswith(".js") or self.path.endswith(".css"):
            # If it's the root or a manifest file, let the standard handler proceed
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # 2. For all other paths (like /profile, /about, etc.), rewrite to index.html
        self.path = "/index.html"
        
        # Now, let the default handler take over, which will serve index.html
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        with open(os.path.join(BUILD_DIR, "index.html"), "rb") as file:
            self.wfile.write(file.read())

# Setup the server
Handler = SPAHandler
Handler.directory = BUILD_DIR

try:
    with socketserver.TCPServer(("", PORT), Handler):
        print(f"Serving React SPA from 'build' directory on http://127.0.0.1:{PORT}")
        print("Press Ctrl+C to stop the server.")
        server_address = ("", PORT)
        httpd = socketserver.TCPServer(server_address, Handler)
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"\nAn error occurred while starting the server: {e}")