#!/usr/bin/env python3
"""
Script de nettoyage des dépendances inutilisées.
Supprime les packages non utilisés et valide les imports.

Usage:
    python cleanup_requirements.py
"""

import subprocess
import sys
from pathlib import Path

# Couleurs pour l'output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def run_command(cmd, description=""):
    """Exécute une commande shell."""
    if description:
        print(f"{YELLOW}[*] {description}...{NC}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{RED}✗ Erreur: {result.stderr}{NC}")
            return False
        return True
    except Exception as e:
        print(f"{RED}✗ Exception: {e}{NC}")
        return False

def uninstall_packages(packages):
    """Désinstalle une liste de packages."""
    print(f"{YELLOW}[1/4] Suppression des packages non utilisés...{NC}")
    for package in packages:
        cmd = f"pip uninstall -y {package} 2>/dev/null"
        subprocess.run(cmd, shell=True, capture_output=True)
    print(f"{GREEN}✓ Packages supprimés{NC}\n")

def install_requirements():
    """Installe les requirements."""
    print(f"{YELLOW}[2/4] Installation des requirements officiels...{NC}")
    if run_command("pip install -r requirements.txt"):
        print(f"{GREEN}✓ Requirements installés{NC}\n")
        return True
    else:
        print(f"{RED}✗ Erreur lors de l'installation{NC}")
        return False

def verify_imports():
    """Vérifie que tous les imports fonctionnent."""
    print(f"{YELLOW}[3/4] Vérification des imports...{NC}")
    
    imports_to_check = [
        ("telethon", "from telethon import TelegramClient, events"),
        ("requests", "import requests"),
        ("PyJWT", "import jwt"),
        ("python-dotenv", "from dotenv import load_dotenv"),
    ]
    
    all_ok = True
    for name, import_stmt in imports_to_check:
        try:
            exec(import_stmt)
            print(f"{GREEN}✓ {name}{NC}")
        except ImportError as e:
            print(f"{RED}✗ {name}: {e}{NC}")
            all_ok = False
    
    print()
    return all_ok

def check_unused_packages():
    """Vérifie la présence de packages non utilisés."""
    print(f"{YELLOW}[4/4] Vérification des packages non utilisés...{NC}")
    
    # Packages qui ne devraient pas être installés
    unused = ["deep-translator", "beautifulsoup4", "soupsieve"]
    
    result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
    installed = result.stdout.lower()
    
    found_unused = []
    for package in unused:
        if package.lower() in installed:
            found_unused.append(package)
    
    if found_unused:
        print(f"{RED}✗ Packages non utilisés détectés: {', '.join(found_unused)}{NC}")
        print(f"  Exécutez: pip uninstall -y {' '.join(found_unused)}")
        return False
    else:
        print(f"{GREEN}✓ Aucun package non utilisé détecté{NC}\n")
        return True

def main():
    """Fonction principale."""
    print(f"\n{YELLOW}{'='*60}{NC}")
    print(f"{YELLOW}  🧹 NETTOYAGE DES DÉPENDANCES{NC}")
    print(f"{YELLOW}{'='*60}{NC}\n")
    
    # Étapes
    packages_to_remove = ["deep-translator", "beautifulsoup4", "soupsieve"]
    
    uninstall_packages(packages_to_remove)
    
    if not install_requirements():
        sys.exit(1)
    
    if not verify_imports():
        sys.exit(1)
    
    if not check_unused_packages():
        print(f"\n{YELLOW}Exécutez manuellement:${NC}")
        print(f"  pip uninstall -y deep-translator beautifulsoup4 soupsieve\n")
    
    # Afficher les packages installés
    print(f"{YELLOW}Packages actuellement installés:{NC}")
    subprocess.run(
        "pip list | grep -E 'telethon|requests|PyJWT|python-dotenv'",
        shell=True
    )
    
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}  🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")

if __name__ == "__main__":
    main()
