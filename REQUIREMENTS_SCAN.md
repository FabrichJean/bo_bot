# 📦 SCAN COMPLET DES REQUIREMENTS - Bobot Project

## 1. REQUIREMENTS PYTHON (External Libraries)

### Dépendances Principales
```
telethon>=1.43.0       # Client Telegram asynchrone
requests>=2.31.0       # HTTP requests library
PyJWT>=2.12.0          # JWT token generation & validation
python-dotenv>=1.0.0   # Environment variables management
```

**Fichiers qui utilisent ces packages:**
- `main.py`: telethon, requests
- `api_client.py`: requests, jwt (PyJWT)
- `token_generator.py`: jwt (PyJWT)
- `browser_sim.py`: asyncio (stdlib)
- `command_handler.py`: asyncio (stdlib)
- `user_registry.py`: json, os (stdlib)

### Dépendances Optionnelles (Screenshots)
```
playwright>=1.45.0     # Browser automation (Python 3.11-3.12)
OR
selenium>=4.0.0        # Browser automation (Python 3.14 alternative)
webdriver-manager>=4.0.0  # Webdriver management
```

**Fichiers qui utilisent ces packages:**
- `browser_sim.py`: playwright.sync_api, playwright.async_api

---

## 2. STANDARD LIBRARY IMPORTS

Python built-in modules utilisés (aucune installation requise):
```
asyncio              # Asynchronous I/O (main.py, browser_sim.py, command_handler.py)
json                 # JSON parsing (user_registry.py)
os                   # OS operations (user_registry.py)
typing               # Type hints (api_client.py, token_generator.py, etc.)
time                 # Time operations (api_client.py, token_generator.py)
```

---

## 3. MODULES LOCAUX (Custom Modules)

Fichiers Python du projet qui s'importent mutuellement:
```
main.py              # Point d'entrée principal
├── from api_client import APIClient
├── from browser_sim import async_screenshot_with_token
├── from token_generator import TokenGenerator
├── from command_handler import CommandHandler
├── from user_registry import UserRegistry
└── from config import *

api_client.py        # Client API
token_generator.py   # JWT token generation
browser_sim.py       # Screenshot automation
command_handler.py   # Command processing
user_registry.py     # User management
config.py            # Configuration centralisée
```

---

## 4. VERSIONS COMPATIBLE

### Python Versions:
- ✅ **Python 3.11-3.12**: Support complet (Playwright + requests)
- ⚠️ **Python 3.14 (alpha)**: Dépendances principales OK (sans Playwright)
- ❌ **Python < 3.10**: Non supporté

### Comparabilité avec Telethon:
```
telethon 1.43.2:
  ✓ Python 3.8+
  ✓ Supporte async/await
  ✓ Nécessite: pyaes, rsa (auto-installés)
```

---

## 5. FICHIERS DE CONFIGURATION

### Environment Variables (.env required)
```
API_ID=37308629              # Telegram API ID
API_HASH=698a893741a1019d   # Telegram API Hash
PHONE_NUMBER=+1234567890    # User phone number
BOT_TOKEN=...               # Optional bot token
```

### Configuration Files:
- `config.py`: Configuration centralisée (JWT_SECRET, BASE_URL, etc.)
- `authorized_users.json`: Liste des utilisateurs autorisés
- `registration_codes.txt`: Codes d'enregistrement uniques
- `ecosystem.config.js`: Configuration PM2 pour déploiement

### Session Files:
- `session_bobot.session`: Telethon session cache
- `session_bobota.session`: Secondary session

---

## 6. INSTALLATION RAPIDE

### Installation complète (Python 3.11-3.12):
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
playwright install
```

### Installation minimale (Python 3.14):
```bash
pip install -r requirements.txt
# Sans screenshots - utiliser Selenium si besoin
```

### Vérification:
```bash
python -c "from telethon import TelegramClient; from api_client import APIClient; print('✅ OK')"
```

---

## 7. DÉPENDANCES TRANSITIVIES (Auto-installées)

Ces packages s'installent automatiquement avec les dépendances principales:
```
telethon → pyaes, rsa
requests → charset-normalizer, idna, urllib3, certifi
playwright → pyee, greenlet
```

---

## 8. RÉCAPITULATIF DES FICHIERS

| Fichier | Type | Dépendances |
|---------|------|-------------|
| main.py | Principal | telethon, requests, config |
| api_client.py | Module | requests, PyJWT |
| token_generator.py | Module | PyJWT |
| browser_sim.py | Module | playwright (optionnel) |
| command_handler.py | Module | asyncio (stdlib) |
| user_registry.py | Module | json, os (stdlib) |
| config.py | Config | Aucune |
| test_*.py | Tests | asyncio (stdlib) |

---

## 9. NOTES IMPORTANTES

1. ⚠️ **Playwright + Python 3.14**: Issue avec greenlet, utiliser requirements-optional.txt
2. 🔐 **Secrets**: Ne pas committer `.env`, `session_*.session`
3. 📁 **Permissions**: Fichiers JSON nécessitent les permissions d'écriture
4. 🔄 **Async**: Tous les imports telethon doivent être en contexte async
5. 💾 **Cache**: Dossier `.venv/` et `__pycache__/` doivent être ignorés

---

## 10. DÉPANNAGE

**ImportError: No module named 'telethon'**
```bash
pip install -r requirements.txt
```

**ImportError: No module named 'playwright'**
```bash
pip install -r requirements-optional.txt
playwright install
```

**Erreur greenlet avec Python 3.14**
```bash
# Utiliser versions binaires uniquement
pip install --only-binary :all: -r requirements-optional.txt
```

---

**Généré le:** 2026-05-13  
**Version du projet:** 1.0.0  
**Python minimum:** 3.11
