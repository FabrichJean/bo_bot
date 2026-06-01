#!/bin/bash

# 🚀 Script d'Installation Automatique
# Ce script configure l'environnement et vérifie les dépendances

echo ""
echo "========================================================================"
echo "  🚀 INSTALLATION ET CONFIGURATION DU SYSTÈME"
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

# Créer le répertoire templates s'il n'existe pas
if [ ! -d "templates" ]; then
    echo ""
    echo "📁 Création du répertoire templates..."
    mkdir -p templates
    echo "   ✅ Répertoire créé"
fi

# Installer les dépendances Python
echo ""
echo "📦 Installation des dépendances Python..."
echo "   Cela peut prendre quelques minutes..."

pip3 install --quiet flask 2>/dev/null && echo "   ✅ Flask" || echo "   ❌ Flask"
pip3 install --quiet telethon 2>/dev/null && echo "   ✅ Telethon" || echo "   ❌ Telethon"
pip3 install --quiet opencc 2>/dev/null && echo "   ✅ OpenCC" || echo "   ❌ OpenCC"

# Vérifier les dépendances
echo ""
echo "🔍 Vérification des dépendances..."
python3 << 'EOF'
import sys

packages = {
    'flask': 'Flask',
    'telethon': 'Telethon',
    'opencc': 'OpenCC'
}

for package, name in packages.items():
    try:
        __import__(package)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name}")
        sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Certaines dépendances ne sont pas installées"
    echo "   Installez manuellement avec:"
    echo "   pip install flask telethon opencc"
    exit 1
fi

# Vérifier l'intégrité du système
echo ""
echo "🔎 Vérification de l'intégrité du système..."
python3 verify_system.py

# Résumé final
echo ""
echo "========================================================================"
echo "  ✅ INSTALLATION TERMINÉE"
echo "========================================================================"
echo ""
echo "🚀 Pour démarrer, exécutez:"
echo ""
echo "   python3 launcher.py"
echo ""
echo "Ou visitez:"
echo "   - Annotation: http://localhost:5000"
echo "   - Test: http://localhost:5001/test"
echo ""
echo "Pour plus d'informations, consultez QUICKSTART.md"
echo ""
