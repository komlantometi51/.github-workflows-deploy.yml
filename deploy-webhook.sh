#!/bin/bash
# Script webhook pour auto-déploiement Git
# Placez ce script sur votre serveur et exposez-le via un serveur HTTP

set -e

# Configuration
REPO_PATH="/var/www/wordpress"
REPO_URL="https://github.com/komlantometi51/.github-workflows-deploy.yml.git"
BRANCH="main"

# Logs
LOG_FILE="/var/log/wordpress-deploy.log"

log() {
    echo "[$(date '%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=== Début du déploiement ==="

# Aller au répertoire du repo
cd "$REPO_PATH" || exit 1

# Mettre à jour depuis Git
log "Mise à jour depuis Git..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Exécuter les commandes de déploiement
log "Installation des dépendances..."
if [ -f "composer.json" ]; then
    composer install --no-dev --optimize-autoloader
fi

# Mettre en cache WordPress
log "Nettoyage du cache..."
wp cache flush --allow-root || true

log "=== Déploiement réussi ==="
echo "OK"
