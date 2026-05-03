#!/usr/bin/env python3
"""
Serveur webhook pour auto-déploiement GitHub
Lancez : python3 webhook-server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import logging

# Configuration
WEBHOOK_PORT = 8000
WEBHOOK_SECRET = "votre_secret_github"  # À définir dans GitHub Settings
DEPLOY_SCRIPT = "/path/to/deploy-webhook.sh"

# Logging
logging.basicConfig(
    filename="/var/log/webhook-deploy.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Gérer les requêtes POST du webhook GitHub"""
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            
            # Vérifier le secret (optionnel)
            signature = self.headers.get('X-Hub-Signature-256', '')
            
            logging.info(f"Webhook reçu - Branche: {payload.get('ref')}")
            
            # Vérifier qu'on est sur main
            if payload.get('ref') != 'refs/heads/main':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Branche ignorée")
                return
            
            # Exécuter le script de déploiement
            logging.info("Démarrage du déploiement...")
            result = subprocess.run(['/bin/bash', DEPLOY_SCRIPT], 
                                    capture_output=True, 
                                    text=True)
            
            if result.returncode == 0:
                logging.info("Déploiement réussi")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Déploiement réussi")
            else:
                logging.error(f"Erreur: {result.stderr}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Erreur de déploiement")
        
        except Exception as e:
            logging.error(f"Erreur: {str(e)}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Erreur serveur")
    
    def log_message(self, format, *args):
        """Supprimer les logs par défaut"""
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', WEBHOOK_PORT), WebhookHandler)
    logging.info(f"Serveur webhook lancé sur le port {WEBHOOK_PORT}")
    print(f"Serveur webhook actif sur http://0.0.0.0:{WEBHOOK_PORT}")
    server.serve_forever()
