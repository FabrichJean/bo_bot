#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 DÉMO INTERACTIVE DU SYSTÈME DE TEST/FEEDBACK

Ce script démontre le cycle complet:
1. Message → Prédiction du modèle
2. Verdict utilisateur (Correct/Corrigé/Faux)
3. Réentraînement automatique
4. Prédictions meilleures pour les messages similaires
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire courant au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rule_engine import RuleEngine, MessageExtractor
from data_annotator import DataAnnotator
from integration_with_main import ModelTesterIntegration

def print_header(text):
    """Affiche un en-tête"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_subheader(text):
    """Affiche un sous-titre"""
    print(f"\n{'─'*70}")
    print(f"  ▶ {text}")
    print(f"{'─'*70}")

def format_result(result):
    """Formate le résultat de prédiction"""
    if not result or "action" not in result:
        return "   ❌ Aucune prédiction"
    
    action = result.get("action", "?")
    target_type = result.get("target_type", "?")
    identifier = result.get("identifier", "?")
    confidence = result.get("confidence", 0) * 100
    
    # Emoji de confiance
    if confidence >= 80:
        conf_emoji = "🟢"
    elif confidence >= 60:
        conf_emoji = "🟡"
    else:
        conf_emoji = "🔴"
    
    return (f"   Action: {action}\n"
            f"   Type: {target_type}\n"
            f"   ID: {identifier}\n"
            f"   {conf_emoji} Confiance: {confidence:.1f}%")

def get_user_verdict():
    """Demande le verdict à l'utilisateur"""
    while True:
        print("\n   Résultat correct? (c=correct, r=corrigé, f=faux, q=quitter)")
        choice = input("   > ").strip().lower()
        
        if choice == "c":
            return "correct", None, None, None
        elif choice == "r":
            print("\n   Entrez la correction:")
            action = input("   Action (activate/deactivate): ").strip() or "?"
            target_type = input("   Type (platform/channel): ").strip() or "?"
            identifier = input("   Identifiant: ").strip() or "?"
            return "corrected", action, target_type, identifier
        elif choice == "f":
            return "wrong", None, None, None
        elif choice == "q":
            return None, None, None, None
        else:
            print("   ❌ Choix invalide")

def main():
    """Fonction principale"""
    
    print_header("🎯 SYSTÈME DE TEST ET FEEDBACK INTERACTIF")
    print("""
Ce système démontre comment:
1. Faire des prédictions avec le modèle
2. Obtenir un retour utilisateur
3. Réentraîner le modèle automatiquement
4. Vérifier les améliorations

Messages d'exemple:
  • 启用 Wangpai 平台     (Activer la plateforme Wangpai)
  • 关闭 ID:156 频道      (Fermer le canal ID:156)
  • 开启 Jincheng 频道    (Ouvrir le canal Jincheng)
""")
    
    # Initialiser le système
    print_subheader("🔧 Initialisation du système")
    try:
        tester = ModelTesterIntegration()
        print(f"   ✅ Système prêt")
        print(f"   📊 Historique: {len(tester.test_history)} tests")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # Boucle interactive
    test_count = 0
    
    while True:
        print_subheader(f"Test #{test_count + 1}")
        
        # Demander le message
        message = input("\n   Entrez un message (ou 'q' pour quitter): ").strip()
        
        if message.lower() == 'q':
            break
        
        if not message:
            print("   ⚠️  Message vide")
            continue
        
        # Faire la prédiction
        print("\n   🤖 Prédiction du modèle:")
        prediction = tester.test_message(message)
        
        if not prediction.get("success"):
            print("   ❌ Aucune prédiction disponible")
            continue
        
        # Afficher le résultat
        print(format_result(prediction["result"]))
        
        # Obtenir le verdict
        verdict, action, ptype, pidentifier = get_user_verdict()
        
        if verdict is None:
            break
        
        # Enregistrer le feedback
        print("\n   ⏳ Enregistrement du feedback et réentraînement...")
        result = tester.record_feedback(
            test_id=prediction["test_id"],
            message=message,
            verdict=verdict,
            corrected_action=action,
            corrected_type=ptype,
            corrected_id=pidentifier
        )
        
        if result.get("success"):
            print(f"   ✅ {result['message']}")
            if result.get("feedback_used_for_training"):
                print("   📈 Modèle réentraîné")
            else:
                print("   ℹ️  Feedback enregistré sans réentraînement")
        
        test_count += 1
    
    # Afficher les statistiques finales
    print_header("📊 STATISTIQUES FINALES")
    
    if len(tester.test_history) == 0:
        print("\n   Aucun test enregistré")
        return
    
    correct_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'correct')
    corrected_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'corrected')
    wrong_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'wrong')
    
    total = len(tester.test_history)
    accuracy = (correct_count + corrected_count) / total * 100 if total > 0 else 0
    
    print(f"\n   📈 Tests effectués: {total}")
    print(f"   ✅ Correct: {correct_count} ({correct_count/total*100:.1f}%)")
    print(f"   ✏️  Corrigé: {corrected_count} ({corrected_count/total*100:.1f}%)")
    print(f"   ❌ Faux: {wrong_count} ({wrong_count/total*100:.1f}%)")
    print(f"\n   🎯 Taux de succès: {accuracy:.1f}%")
    
    # Message de conclusion
    if accuracy >= 90:
        print("\n   🌟 Excellent! Le modèle fonctionne très bien.")
    elif accuracy >= 75:
        print("\n   👍 Bon! Le modèle fonctionne correctement.")
    elif accuracy >= 60:
        print("\n   ⚠️  Acceptable. Continuez les tests pour améliorer.")
    else:
        print("\n   📚 Besoin de plus d'entraînement. Collectez plus de données.")
    
    print_header("✨ FIN DE LA DÉMONSTRATION")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interruption de l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
