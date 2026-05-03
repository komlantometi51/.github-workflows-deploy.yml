#!/usr/bin/env python3
"""
Webhook server for automatic GitHub deployment
Run: python3 webhook-server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import logging

# Configuration
WEBHOOK_PORT = 8000
WEBHOOK_SECRET = "your_github_secret"  # Set in GitHub Settings
DEPLOY_SCRIPT = "/workspaces/.github-workflows-deploy.yml/deploy-webhook.sh"

# Logging
logging.basicConfig(
    filename="/tmp/webhook-deploy.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests from GitHub webhook"""
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            
            # Check secret (optional)
            signature = self.headers.get('X-Hub-Signature-256', '')
            
            logging.info(f"Webhook received - Branch: {payload.get('ref')}")
            
            # Verify we are on main branch
            if payload.get('ref') != 'refs/heads/main':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Branch ignored")
                return
            
            # Execute deployment script
            logging.info("Starting deployment...")
            result = subprocess.run(['/bin/bash', DEPLOY_SCRIPT], 
                                    capture_output=True, 
                                    text=True)
            
            if result.returncode == 0:
                logging.info("Deployment successful")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Deployment successful")
            else:
                logging.error(f"Error: {result.stderr}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Deployment error")
        
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server error")
    
    def log_message(self, format, *args):
        """Suppress default logs"""
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', WEBHOOK_PORT), WebhookHandler)
    logging.info(f"Webhook server started on port {WEBHOOK_PORT}")
    print(f"Webhook server active on http://0.0.0.0:{WEBHOOK_PORT}")
    server.serve_forever()
