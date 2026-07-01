#!/bin/bash

# 🚀 Script d'Installation Automatique
# Configure l'environnement et installe les dépendances du bot Telegram

echo ""
echo "========================================================================"
echo "  🚀 INSTALLATION ET CONFIGURATION DU BOT"
echo "========================================================================"
echo ""

# Vérifier Python
echo "✅ Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "   $PYTHON_VERSION"

# Détecter le venv utilisé pour faire tourner le bot (ex: ecosystem.config.js
# pointe vers venv/bin/python en prod). Sans ça, "pip3" peut installer dans le
# mauvais Python et le bot ne trouve jamais les packages au démarrage.
PIP_BIN="pip3"
PYTHON_BIN="python3"
if [ -x "venv/bin/pip" ]; then
    PIP_BIN="venv/bin/pip"
    PYTHON_BIN="venv/bin/python"
    echo "   📦 venv détecté : venv/"
elif [ -x ".venv/bin/pip" ]; then
    PIP_BIN=".venv/bin/pip"
    PYTHON_BIN=".venv/bin/python"
    echo "   📦 venv détecté : .venv/"
else
    echo "   ⚠️  Aucun venv trouvé (venv/ ou .venv/) — installation avec pip3 global"
fi

# Installer les dépendances Python depuis requirements.txt
echo ""
echo "📦 Installation des dépendances Python (requirements.txt)..."
echo "   Avec : $PIP_BIN"
echo "   Cela peut prendre quelques minutes..."

if ! "$PIP_BIN" install -r requirements.txt; then
    echo ""
    echo "❌ Échec de l'installation des dépendances"
    echo "   Installez manuellement avec: $PIP_BIN install -r requirements.txt"
    exit 1
fi

echo "   ✅ Dépendances installées"

# Installer le navigateur Playwright (nécessaire pour la feature screenshot)
echo ""
echo "🌐 Installation du navigateur Playwright (Chromium)..."
if ! "$PYTHON_BIN" -m playwright install chromium; then
    echo "   ⚠️  Échec de l'installation de Chromium — la feature screenshot ne fonctionnera pas"
fi

# Résumé final
echo ""
echo "========================================================================"
echo "  ✅ INSTALLATION TERMINÉE"
echo "========================================================================"
echo ""
echo "🚀 Pour démarrer le bot, exécutez :"
echo ""
echo "   $PYTHON_BIN main.py"
echo ""
echo "   (redémarrez pm2 si le bot tourne déjà en prod : pm2 restart bo-bot)"
echo ""
echo "📱 L'app Android compagnon (alarme + configuration) se trouve dans"
echo "   android_alarm_app/ — à ouvrir dans Android Studio"
echo "   (voir android_alarm_app/README.md pour le premier lancement)."
echo ""
