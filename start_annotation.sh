#!/bin/bash
# Script de démarrage du système d'annotation
# Usage: bash start_annotation.sh

echo "🎯 Système d'Annotation de Données Chinoises"
echo "==========================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non installé"
    exit 1
fi

echo "✅ Python3 détecté"

# Vérifier/installer dépendances
echo ""
echo "📦 Installation des dépendances..."
pip install flask >/dev/null 2>&1
pip install opencc >/dev/null 2>&1
echo "✅ Dépendances installées"

# Vérifier templates
if [ ! -d "templates" ]; then
    echo ""
    echo "❌ Dossier 'templates' non trouvé"
    echo "   Créez le dossier templates/ avec les fichiers HTML"
    exit 1
fi

echo "✅ Templates trouvés"

# Lancer l'app
echo ""
echo "🚀 Démarrage de l'application..."
echo ""
echo "   🌐 Ouvrez: http://localhost:5000"
echo "   📝 Pour annoter: http://localhost:5000/annotate"
echo "   📊 Pour statistiques: http://localhost:5000/stats"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 annotation_app.py
