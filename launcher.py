#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script de Lancement Principal

Gère le démarrage des différentes composants du système
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

def print_banner(text):
    """Affiche une bannière"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    print_banner("✅ Vérification des dépendances")
    
    required = ["flask", "telethon", "opencc"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Paquets manquants: {', '.join(missing)}")
        print(f"\n   Installez avec:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("\n✅ Toutes les dépendances sont installées")
    return True

def check_data_files():
    """Vérifie que les fichiers de données existent"""
    print_banner("📊 Vérification des données")
    
    required_files = [
        "training_data.json",
        "annotated_messages.json",
        "sample_messages_zh.json"
    ]
    
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✅ {filename} ({size} bytes)")
        else:
            print(f"  ⚠️  {filename} (manquant - créé au premier lancement)")
    
    return True

def launch_annotation_app():
    """Lance l'application d'annotation"""
    print_banner("📝 Lancement de l'Application d'Annotation")
    print("  Port: 5000")
    print("  URL: http://localhost:5000")
    print("  Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        subprocess.run([sys.executable, "annotation_app.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n  Arrêt de l'application d'annotation")

def launch_model_tester():
    """Lance l'interface de test du modèle"""
    print_banner("🧪 Lancement de l'Interface de Test")
    print("  Port: 5001")
    print("  URL: http://localhost:5001/test")
    print("  Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        subprocess.run([sys.executable, "model_tester.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n  Arrêt de l'interface de test")

def launch_demo():
    """Lance la démo interactive"""
    print_banner("🎮 Lancement de la Démo Interactive")
    
    try:
        subprocess.run([sys.executable, "demo_feedback.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n  Démo interrompue par l'utilisateur")

def launch_test():
    """Lance le test du cycle complet"""
    print_banner("🧪 Test du Cycle Complet de Feedback")
    
    try:
        subprocess.run([sys.executable, "test_feedback_loop.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n  Test interrompu par l'utilisateur")

def show_menu():
    """Affiche le menu principal"""
    print_banner("🎯 SYSTÈME D'ANNOTATION ET TEST")
    
    print("""
Choisissez une option:

  1. 📝 Annotation (Web) - Annoter les messages
  2. 🧪 Test & Feedback - Tester le modèle
  3. 🎮 Démo Interactive - CLI interactive
  4. 🧪 Test Complet - Valider le cycle
  5. 📊 Checker l'état - Vérifier les données
  6. ❌ Quitter

""")

def check_status():
    """Affiche l'état du système"""
    print_banner("📊 État du Système")
    
    # Vérifier les données
    files_status = {}
    for filename in ["training_data.json", "annotated_messages.json", "test_feedback.json"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            files_status[filename] = f"✅ ({size} bytes)"
        else:
            files_status[filename] = "❌ (manquant)"
    
    print("\nFichiers de données:")
    for name, status in files_status.items():
        print(f"  {name}: {status}")
    
    # Compter les annotations
    import json
    annotations = 0
    feedback = 0
    
    try:
        with open("annotated_messages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            annotations = len(data.get("annotated_messages", []))
            feedback = len(data.get("feedback", []))
    except:
        pass
    
    print(f"\nStatistiques:")
    print(f"  Messages annotés: {annotations}")
    print(f"  Feedback collectés: {feedback}")
    
    # Afficher les suggestions
    print(f"\nSuggestions:")
    if annotations < 10:
        print("  ⚠️  Besoin de plus de messages annotés (< 10)")
        print("     Lancez l'application d'annotation")
    else:
        print(f"  ✅ Suffisamment de messages annotés ({annotations})")
    
    if feedback < 5:
        print("  ⚠️  Besoin de plus de feedback (< 5)")
        print("     Lancez la démo interactive ou l'interface de test")
    else:
        print(f"  ✅ Suffisamment de feedback ({feedback})")

def main():
    """Fonction principale"""
    
    print_banner("🚀 LANCEUR SYSTÈME")
    
    # Parser les arguments
    parser = argparse.ArgumentParser(description="Lanceur du système d'annotation")
    parser.add_argument("--annotation", action="store_true", help="Lancer l'app d'annotation")
    parser.add_argument("--test", action="store_true", help="Lancer l'interface de test")
    parser.add_argument("--demo", action="store_true", help="Lancer la démo")
    parser.add_argument("--full-test", action="store_true", help="Lancer le test complet")
    parser.add_argument("--check", action="store_true", help="Vérifier l'état")
    parser.add_argument("--install", action="store_true", help="Vérifier les dépendances")
    
    args = parser.parse_args()
    
    # Mode non-interactif
    if args.install:
        check_dependencies()
        return
    
    if args.annotation:
        launch_annotation_app()
        return
    
    if args.test:
        launch_model_tester()
        return
    
    if args.demo:
        launch_demo()
        return
    
    if args.full_test:
        launch_test()
        return
    
    if args.check:
        check_dependencies()
        check_data_files()
        check_status()
        return
    
    # Mode interactif
    while True:
        show_menu()
        choice = input("Votre choix (1-6): ").strip()
        
        if choice == "1":
            launch_annotation_app()
        elif choice == "2":
            launch_model_tester()
        elif choice == "3":
            launch_demo()
        elif choice == "4":
            launch_test()
        elif choice == "5":
            check_dependencies()
            check_data_files()
            check_status()
        elif choice == "6":
            print("\n👋 Au revoir!")
            break
        else:
            print("\n❌ Option invalide")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interruption de l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
