import requests
import base64
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Default rclone client credentials
CLIENT_ID = "202264815644.apps.googleusercontent.com"
CLIENT_SECRET = "X4Z3ca8xfWDb1Voo-F9a7ZxJ"

# OAuth endpoints
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:8081"
SCOPE = "https://www.googleapis.com/auth/drive"

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract code from query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_components:
            # Get the authorization code
            auth_code = query_components['code'][0]
            
            # Exchange auth code for tokens
            data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': auth_code,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(TOKEN_URL, data=data)
            tokens = response.json()
            
            # Save tokens to file
            with open('tokens.json', 'w') as f:
                json.dump(tokens, f, indent=4)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")
            
            # Stop the server
            raise KeyboardInterrupt

def get_authorization():
    # Generate authorization URL
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    
    # Open browser for authorization
    print("Opening browser for authorization...")
    webbrowser.open(auth_url)
    
    # Start local server to receive callback
    server = HTTPServer(('localhost', 8081), AuthHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nAuthorization complete! Check tokens.json for your refresh token.")

if __name__ == "__main__":
    get_authorization() 