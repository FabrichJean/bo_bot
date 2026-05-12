# BoBot - Installation Guide

## Installation des dépendances principales

```bash
pip install -r requirements.txt
```

Les packages installés:
- **telethon** (>=1.43.0): Client Telegram asynchrone
- **requests** (>=2.31.0): Requêtes HTTP
- **PyJWT** (>=2.12.0): Génération de tokens JWT
- **python-dotenv** (>=1.0.0): Gestion des variables d'environnement

## Installation des dépendances optionnelles (captures d'écran)

### Pour Python 3.11/3.12 (macOS/Linux):

```bash
pip install -r requirements-optional.txt
playwright install
```

### Pour Python 3.14 (alpha):

```bash
pip install selenium>=4.0.0 webdriver-manager>=4.0.0
```

## Vérification de l'installation

```bash
python -c "from telethon import TelegramClient; print('✅ Installation OK')"
```

## Configuration

1. Créez un fichier `.env` à la racine du projet:
```bash
API_ID=votre_api_id
API_HASH=votre_api_hash
PHONE_NUMBER=votre_numero_telegram
```

2. Executez le bot:
```bash
python main.py
```

## Dépannage

**Erreur "ModuleNotFoundError: No module named 'telethon'"**
- Vérifiez que les dépendances sont installées: `pip install -r requirements.txt`

**Erreur Playwright: "playwright install"**
- Installez les navigateurs: `playwright install`

**Python 3.14 + Playwright = Erreur de compilation greenlet**
- Utilisez Selenium à la place ou utilisez Python 3.11/3.12
