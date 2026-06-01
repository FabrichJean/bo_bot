#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Vérification de l'intégrité du système

Ce script vérifie que tous les composants sont en place
"""

import os
import json
import sys

def check_file(filename, file_type="File"):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filename):
        if filename.endswith(".json"):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    json.load(f)
                return f"✅ {file_type}: {filename}"
            except:
                return f"⚠️  {file_type}: {filename} (JSON invalide)"
        else:
            size = os.path.getsize(filename)
            return f"✅ {file_type}: {filename} ({size} bytes)"
    else:
        return f"❌ {file_type}: {filename} (MANQUANT)"

def main():
    """Vérifie tous les fichiers"""
    
    print("\n" + "="*70)
    print("  ✅ VÉRIFICATION DE L'INTÉGRITÉ DU SYSTÈME")
    print("="*70 + "\n")
    
    all_ok = True
    
    # 1. Fichiers Python Core
    print("📦 FICHIERS PYTHON CORE")
    print("-" * 70)
    
    core_files = [
        ("rule_engine.py", "Module"),
        ("data_annotator.py", "Module"),
        ("system_config.py", "Config"),
        ("integration_with_main.py", "Module"),
    ]
    
    for filename, ftype in core_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    # 2. Applications Web
    print("\n🌐 APPLICATIONS WEB")
    print("-" * 70)
    
    web_files = [
        ("annotation_app.py", "App"),
        ("model_tester.py", "App"),
    ]
    
    for filename, ftype in web_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    # 3. Scripts de Test/Démo
    print("\n🧪 SCRIPTS DE TEST/DÉMO")
    print("-" * 70)
    
    test_files = [
        ("demo_feedback.py", "Demo"),
        ("test_feedback_loop.py", "Test"),
        ("test_annotator.py", "Test"),
        ("launcher.py", "Launcher"),
    ]
    
    for filename, ftype in test_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    # 4. Templates HTML
    print("\n🎨 TEMPLATES HTML")
    print("-" * 70)
    
    template_files = [
        ("templates/index.html", "Template"),
        ("templates/annotate.html", "Template"),
        ("templates/stats.html", "Template"),
        ("templates/test.html", "Template"),
        ("templates/test_results.html", "Template"),
        ("templates/test_history.html", "Template"),
    ]
    
    for filename, ftype in template_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    # 5. Fichiers de Données
    print("\n📊 FICHIERS DE DONNÉES")
    print("-" * 70)
    
    data_files = [
        ("sample_messages_zh.json", "Data"),
    ]
    
    optional_data = [
        ("training_data.json", "Data (créé au premier lancement)"),
        ("annotated_messages.json", "Data (créé au premier lancement)"),
        ("test_feedback.json", "Data (créé au premier lancement)"),
    ]
    
    for filename, ftype in data_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    print("\n  Fichiers optionnels (créés au premier lancement):")
    for filename, ftype in optional_data:
        result = check_file(filename, ftype)
        print(f"  {result}")
    
    # 6. Documentation
    print("\n📚 DOCUMENTATION")
    print("-" * 70)
    
    doc_files = [
        ("QUICKSTART.md", "Guide"),
        ("README_COMPLETE.md", "Guide"),
        ("README_ANNOTATION.md", "Guide"),
        ("ANNOTATION_GUIDE.md", "Guide"),
        ("LEARNING_SYSTEM_DOC.md", "Guide"),
        ("SYSTEM_SUMMARY.md", "Guide"),
        ("PROJECT_SUMMARY.md", "Guide"),
        ("INDEX.md", "Index"),
    ]
    
    for filename, ftype in doc_files:
        result = check_file(filename, ftype)
        print(f"  {result}")
        if result.startswith("❌"):
            all_ok = False
    
    # 7. Résumé
    print("\n" + "="*70)
    
    if all_ok:
        print("  ✅ TOUS LES FICHIERS ESSENTIELS SONT PRÉSENTS")
        print("\n  Vous pouvez démarrer avec:")
        print("    python launcher.py")
    else:
        print("  ⚠️  CERTAINS FICHIERS SONT MANQUANTS")
        print("\n  Veuillez vérifier les fichiers marqués avec ❌")
    
    print("="*70 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
