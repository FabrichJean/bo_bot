# 📦 REQUIREMENTS - Bobot Project

## 🎯 Quick Start

### Installation (Python 3.11+)
```bash
pip install -r requirements.txt
```

### Installation with Screenshots (Python 3.11-3.13)
```bash
pip install -r requirements.txt -r requirements-optional.txt
playwright install
```

---

## 📋 Dépendances Principales

| Package | Version | Rôle |
|---------|---------|------|
| **telethon** | >=1.43.0 | Client Telegram asynchrone |
| **requests** | >=2.34.0 | Requêtes HTTP & Google Translate API |
| **PyJWT** | >=2.12.0 | Génération de tokens JWT |
| **python-dotenv** | >=1.0.0 | Chargement du fichier .env |

### Total: 4 dépendances directes
- ~50MB d'espace disque
- ~2-3 minutes d'installation

---

## 🎨 Dépendances Optionnelles

### Pour les captures d'écran:
```bash
pip install -r requirements-optional.txt
playwright install
```

**Fichier:** `requirements-optional.txt`
```ini
playwright>=1.45.0
```

---

## ⚠️ Packages à SUPPRIMER

Les packages suivants ont été détectés comme **NON UTILISÉS**:
- ❌ deep-translator
- ❌ beautifulsoup4
- ❌ soupsieve

### Nettoyage automatique:
```bash
# Python (Recommandé)
python cleanup_requirements.py

# Ou manuellement
pip uninstall -y deep-translator beautifulsoup4 soupsieve
```

### Bash (Alternative)
```bash
bash cleanup_requirements.sh
```

---

## 📁 Fichiers de Configuration

### requirements.txt
✅ Dépendances **OBLIGATOIRES**
- Toujours installer

### requirements-optional.txt
📸 Dépendances **OPTIONNELLES** (screenshots)
- Installer si besoin de captures d'écran

### cleanup_requirements.py
🧹 Script de nettoyage Python
- Supprime les packages inutilisés
- Valide les imports
- Affiche les packages installés

### cleanup_requirements.sh
🧹 Script de nettoyage Bash
- Alternative bash du script Python

---

## 🔍 Détails par Fichier Python

### main.py
```python
from telethon import TelegramClient, events  # ✓ telethon
import requests                               # ✓ requests
from api_client import APIClient              # Local
from browser_sim import async_screenshot...  # ✓ playwright (optionnel)
from token_generator import TokenGenerator   # Local
from command_handler import CommandHandler   # Local
from user_registry import UserRegistry       # Local
from config import *                         # Local
```

### api_client.py
```python
import requests                               # ✓ requests
import jwt                                    # ✓ PyJWT
```

### token_generator.py
```python
import jwt                                    # ✓ PyJWT
```

### browser_sim.py
```python
from playwright.sync_api import sync_playwright      # ✓ playwright (optionnel)
from playwright.async_api import async_playwright    # ✓ playwright (optionnel)
```

### user_registry.py, command_handler.py
Utilisent seulement la **stdlib** (json, os, asyncio, typing)

---

## 🚀 Installation par Cas d'Usage

### 1️⃣ Développement Local (Complet)
```bash
pip install -r requirements.txt -r requirements-optional.txt
playwright install
```
✓ Tous les features disponibles  
✓ Screenshots fonctionnels

### 2️⃣ Production (Minimal)
```bash
pip install -r requirements.txt
```
✓ Juste le bot  
✗ Pas de screenshots (optionnel)

### 3️⃣ Python 3.14 (Alpha)
```bash
pip install --only-binary :all: -r requirements.txt
pip install selenium webdriver-manager
```
✓ Compatible avec Python 3.14  
✓ Pas de problème greenlet

### 4️⃣ Après Cleanup
```bash
python cleanup_requirements.py
```
✓ Supprime deep-translator, beautifulsoup4  
✓ Valide tous les imports  
✓ Affiche l'état final

---

## ✅ Vérification

### Vérifier l'installation:
```bash
python -c "from telethon import TelegramClient; print('✅ OK')"
```

### Vérifier toutes les dépendances:
```bash
python -c "
from telethon import TelegramClient
import requests
import jwt
from dotenv import load_dotenv
print('✅ Toutes les dépendances sont OK')
"
```

### Lister les packages:
```bash
pip list | grep -E 'telethon|requests|PyJWT|python-dotenv'
```

---

## 📊 Statistiques

| Métrique | Valeur |
|----------|--------|
| Dépendances directes | 4 |
| Dépendances transitoires | ~10 |
| Packages mal installés | 0 |
| Packages inutilisés | 3 |
| Taille totale | ~150MB |
| Temps installation | 2-3 min |

---

## 🔗 Fichiers Connexes

- 📄 **REQUIREMENTS_SCAN.md** - Scan détaillé de tous les imports
- 📄 **REQUIREMENTS_REPORT.md** - Rapport complet de l'audit
- 📄 **REQUIREMENTS_AUDIT.md** - Audit des dépendances
- 📄 **INSTALLATION.md** - Guide d'installation
- 🐍 **cleanup_requirements.py** - Script Python de nettoyage
- 🐚 **cleanup_requirements.sh** - Script Bash de nettoyage

---

## 🐛 Dépannage

### ImportError: No module named 'telethon'
```bash
pip install -r requirements.txt
```

### ImportError: No module named 'playwright'
```bash
pip install -r requirements-optional.txt
playwright install
```

### Erreur "playwright install" failed
```bash
# Pour Python 3.14
pip install --only-binary :all: playwright
```

### Packages fantômes détectés
```bash
# Nettoyer les packages inutilisés
python cleanup_requirements.py
```

---

## 📌 Résumé Final

✅ **requirements.txt** - 4 packages, 100% documentés  
✅ **requirements-optional.txt** - Playwright pour screenshots  
✅ **Aucune dépendance manquante**  
✅ **Tous les imports testés**  
✅ **Compatible Python 3.11-3.14**  

---

**Dernière mise à jour:** 13 Mai 2026  
**Status:** ✅ Validé et prêt pour production
