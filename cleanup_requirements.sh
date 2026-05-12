#!/bin/bash

# Script de nettoyage des dépendances inutilisées
# Utilisation: ./cleanup_requirements.sh

echo "🧹 Nettoyage des dépendances inutilisées..."
echo ""

# Couleurs pour l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/3] Suppression des packages non utilisés...${NC}"
pip uninstall -y deep-translator beautifulsoup4 soupsieve 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Packages supprimés${NC}"
else
    echo -e "${YELLOW}⚠ Aucun package à supprimer${NC}"
fi

echo ""
echo -e "${YELLOW}[2/3] Installation des requirements officiels...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Requirements installés${NC}"
else
    echo -e "${RED}✗ Erreur lors de l'installation${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[3/3] Vérification de l'installation...${NC}"
python -c "
from telethon import TelegramClient, events
import requests
import jwt
from dotenv import load_dotenv
print('✓ telethon')
print('✓ requests')
print('✓ PyJWT')
print('✓ python-dotenv')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tous les imports fonctionnent${NC}"
    echo ""
    echo -e "${GREEN}🎉 Nettoyage terminé avec succès!${NC}"
    echo ""
    echo "Packages actuellement installés:"
    pip list | grep -E "telethon|requests|PyJWT|python-dotenv"
else
    echo -e "${RED}✗ Erreur lors de la vérification${NC}"
    exit 1
fi
