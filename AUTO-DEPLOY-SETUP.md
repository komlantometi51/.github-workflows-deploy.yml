# Guide d'Auto-Déploiement Git

## 📋 Vue d'ensemble

Ce guide configure un système d'auto-déploiement où chaque `push` vers `main` déclenche automatiquement le déploiement sur votre serveur.

---

## 🔧 Configuration (3 étapes)

### **1️⃣ Sur GitHub - Ajouter le Webhook**

1. Allez sur votre dépôt : `https://github.com/komlantometi51/.github-workflows-deploy.yml`
2. **Settings** → **Webhooks** → **Add webhook**
3. Remplissez :
   - **Payload URL** : `https://votre-serveur.com:8000/` (URL publique de votre serveur)
   - **Content type** : `application/json`
   - **Events** : `Push events`
   - **Secret** : (optionnel) entrez une clé secrète

4. Cliquez **Add webhook** ✅

---

### **2️⃣ Sur le Serveur - Installer le Serveur Webhook**

```bash
# Téléchargez les scripts
cd /home/wordpress  # ou votre chemin
git clone https://github.com/komlantometi51/.github-workflows-deploy.yml.git
cd .github-workflows-deploy.yml

# Rendez les scripts exécutables
chmod +x deploy-webhook.sh webhook-server.py

# Installez les dépendances (si nécessaire)
# Pour Debian/Ubuntu :
sudo apt-get install python3 git curl

# Lancez le serveur webhook en arrière-plan
python3 webhook-server.py &

# Ou avec systemd (recommandé) :
sudo nano /etc/systemd/system/webhook-deploy.service
```

**Contenu du fichier service :**
```ini
[Unit]
Description=WordPress Deploy Webhook Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/repo
ExecStart=/usr/bin/python3 /path/to/webhook-server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer le service
sudo systemctl enable webhook-deploy.service
sudo systemctl start webhook-deploy.service
sudo systemctl status webhook-deploy.service
```

---

### **3️⃣ Configurer le Script de Déploiement**

Modifiez `deploy-webhook.sh` :
```bash
REPO_PATH="/var/www/wordpress"  # Chemin de votre site
REPO_URL="https://..."          # URL du dépôt
```

---

## ✅ Tester le Déploiement

### **Test 1 : Depuis GitHub**
1. Va sur votre dépôt
2. **Webhooks** → Sélectionnez le webhook
3. **Recent Deliveries** → Cliquez sur une livraison → **Redeliver**

### **Test 2 : Faire un push**
```bash
cd /workspaces/.github-workflows-deploy.yml
echo "test" >> test.txt
git add test.txt
git commit -m "Test déploiement"
git push origin main
```

Vérifiez les logs du serveur :
```bash
tail -f /var/log/webhook-deploy.log
```

---

## 🔐 Sécurité

- **Port** : Exposez le port 8000 (ou changez dans le code)
- **Firewall** : Autorisez uniquement GitHub IP (140.82.112.0/20, etc.)
- **Secret** : Utilisez `X-Hub-Signature-256` dans les headers

---

## 📊 Variables de Déploiement

Dans [deploy.yml](.github/workflows/deploy.yml), vous pouvez ajouter des secrets GitHub :

```bash
Settings → Secrets and variables → Actions → New secret
```

Secrets utiles :
- `WEBHOOK_URL` : URL publique du webhook
- `DEPLOY_SECRET` : Clé secrète du webhook
- `FTP_SERVER`, `FTP_USER`, `FTP_PASS` : Pour FTP

---

## 🆘 Dépannage

**Le webhook ne déclenche pas ?**
- Vérifiez le port 8000 est ouvert : `netstat -tulpn | grep 8000`
- Testez la connexion : `curl http://localhost:8000`
- Vérifiez les logs : `tail -f /var/log/webhook-deploy.log`

**Erreur Git lors du déploiement ?**
```bash
# Assurez-vous que l'utilisateur www-data a accès au repo
sudo chown -R www-data:www-data /path/to/repo
```

---

## 📝 Variables d'Environnement

Modifiez dans `webhook-server.py` :
```python
WEBHOOK_PORT = 8000
DEPLOY_SCRIPT = "/path/to/deploy-webhook.sh"
```

---

**Le déploiement automatique est maintenant actif ! 🚀**
