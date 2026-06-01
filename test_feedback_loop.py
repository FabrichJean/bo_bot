#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du cycle de feedback complet:
1. Message → Prédiction
2. Verdict utilisateur (Correct/Corrigé/Faux)
3. Entraînement du modèle
4. Vérification que la confiance augmente
"""

import json
import time
import sys
import os

# Ajouter le répertoire parent au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_annotator import DataAnnotator
from rule_engine import RuleEngine, MessageExtractor

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(num, title):
    """Affiche une étape"""
    print(f"\n[{num}] {title}")
    print("-" * 40)

def main():
    """Test le cycle de feedback complet"""
    
    print_section("🧪 TEST DU CYCLE DE FEEDBACK")
    
    # Initialiser les systèmes
    print_step(1, "Initialisation des systèmes")
    
    try:
        annotator = DataAnnotator()
        print(f"✅ DataAnnotator chargé ({len(annotator.annotations)} annotations)")
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
        annotator = DataAnnotator()
    
    try:
        engine = RuleEngine()
        engine.load_rules()
        print(f"✅ RuleEngine chargé ({len(engine.rules)} règles)")
    except Exception as e:
        print(f"⚠️  Pas de règles existantes, création d'une nouvelle instance")
        engine = RuleEngine()
        engine.rules = []
    
    # Créer des données d'entraînement initiales si nécessaire
    if not engine.rules:
        print_step(2, "Création de règles initiales")
        engine.rules = [
            {"keyword": "启用", "action": "activate", "confidence": 0.85, "examples": ["启用", "打开", "开启"], "target_type": None, "identifier": None},
            {"keyword": "关闭", "action": "deactivate", "confidence": 0.85, "examples": ["关闭", "禁用", "停用"], "target_type": None, "identifier": None},
            {"keyword": "频道", "action": None, "confidence": 0.90, "examples": ["频道", "Channel", "ch"], "target_type": "channel", "identifier": None},
            {"keyword": "平台", "action": None, "confidence": 0.85, "examples": ["平台", "Platform", "Plat"], "target_type": "platform", "identifier": None},
            {"keyword": "ID", "action": None, "confidence": 0.95, "examples": ["ID", "id", "号"], "target_type": None, "identifier": "id"}
        ]
        print("✅ Règles initiales créées")
        engine.save_rules()
    
    # Messages de test
    test_messages = [
        {
            "message": "启用 Wangpai 平台",
            "expected_action": "activate",
            "expected_type": "platform",
            "expected_id": "Wangpai"
        },
        {
            "message": "关闭 ID:156 频道",
            "expected_action": "deactivate",
            "expected_type": "channel",
            "expected_id": "156"
        },
        {
            "message": "开启 Jincheng 频道",
            "expected_action": "activate",
            "expected_type": "channel",
            "expected_id": "Jincheng"
        }
    ]
    
    # Test 1: Prédictions initiales
    print_step(3, "Prédictions AVANT feedback")
    
    predictions_before = []
    for i, test in enumerate(test_messages):
        msg = test["message"]
        result = MessageExtractor.extract_components(msg)
        
        print(f"\n  Message: {msg}")
        if result:
            pred_action = result.get("action", "?")
            pred_type = result.get("target_type", "?")
            pred_id = result.get("identifier", "?")
            confidence = result.get("confidence", 0)
            
            print(f"  ➜ Action: {pred_action} | Type: {pred_type} | ID: {pred_id}")
            print(f"  ⭐ Confiance: {confidence*100:.1f}%")
            
            predictions_before.append({
                "message": msg,
                "result": result,
                "confidence_before": confidence
            })
        else:
            print(f"  ❌ Aucune prédiction")
            predictions_before.append({
                "message": msg,
                "result": None,
                "confidence_before": 0
            })
    
    # Test 2: Feedback et entraînement
    print_step(4, "Application du FEEDBACK et réentraînement")
    
    for i, pred in enumerate(predictions_before):
        msg = pred["message"]
        test = test_messages[i]
        
        print(f"\n  Message: {msg}")
        
        # Simuler un retour utilisateur "corrected"
        feedback_entry = {
            "message": msg,
            "user_verdict": "correct",
            "corrected_action": test["expected_action"],
            "corrected_target_type": test["expected_type"],
            "corrected_identifier": test["expected_id"],
            "confidence": pred["confidence_before"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Ajouter au feedback
        if "feedback" not in annotator.annotations:
            annotator.annotations["feedback"] = []
        annotator.annotations["feedback"].append(feedback_entry)
        
        # Entraîner le modèle avec le feedback
        _train_model_with_feedback(engine, feedback_entry, annotator)
        
        print(f"  ✅ Feedback enregistré et modèle réentraîné")
    
    # Sauvegarder les changements
    engine.save_rules()
    
    # Test 3: Prédictions après feedback
    print_step(5, "Prédictions APRÈS feedback")
    
    predictions_after = []
    for i, test in enumerate(test_messages):
        msg = test["message"]
        result = MessageExtractor.extract_components(msg)
        
        print(f"\n  Message: {msg}")
        if result:
            pred_action = result.get("action", "?")
            pred_type = result.get("target_type", "?")
            pred_id = result.get("identifier", "?")
            confidence = result.get("confidence", 0)
            
            print(f"  ➜ Action: {pred_action} | Type: {pred_type} | ID: {pred_id}")
            print(f"  ⭐ Confiance: {confidence*100:.1f}%")
            
            confidence_before = predictions_before[i]["confidence_before"]
            improvement = (confidence - confidence_before) * 100
            
            if improvement > 0:
                print(f"  📈 Amélioration: +{improvement:.1f}%")
            elif improvement < 0:
                print(f"  📉 Régression: {improvement:.1f}%")
            else:
                print(f"  ➡️  Pas de changement")
            
            predictions_after.append({
                "message": msg,
                "result": result,
                "confidence_after": confidence,
                "improvement": improvement
            })
    
    # Résumé
    print_step(6, "RÉSUMÉ DES RÉSULTATS")
    
    total_improvement = sum(p["improvement"] for p in predictions_after)
    avg_improvement = total_improvement / len(predictions_after) if predictions_after else 0
    
    print(f"\n  Total des améliorations: +{total_improvement:.1f}%")
    print(f"  Amélioration moyenne: +{avg_improvement:.1f}%")
    print(f"  Nombre de messages testés: {len(test_messages)}")
    
    # Vérifier que le feedback a amélioré les prédictions
    if avg_improvement > 0:
        print("\n  ✅ SUCCESS: Le modèle s'est amélioré grâce au feedback!")
    else:
        print("\n  ⚠️  WARNING: Le modèle ne s'est pas amélioré.")
    
    print_section("✨ TEST TERMINÉ")

def _train_model_with_feedback(engine, feedback_entry, annotator):
    """
    Entraîne le modèle avec le feedback utilisateur
    
    Améliore les règles existantes ou en ajoute de nouvelles
    """
    verdict = feedback_entry.get("user_verdict")
    message = feedback_entry.get("message")
    corrected_action = feedback_entry.get("corrected_action")
    corrected_type = feedback_entry.get("corrected_target_type")
    corrected_id = feedback_entry.get("corrected_identifier")
    
    if verdict == "correct":
        # Le modèle était correct - augmenter la confiance
        matching_rules = engine.find_matching_rules(message)
        for rule in matching_rules:
            if rule["action"] == corrected_action:
                rule["confidence"] = min(1.0, rule["confidence"] + 0.03)
                if message not in rule["examples"]:
                    rule["examples"].append(message)
    
    elif verdict == "corrected":
        # L'utilisateur a corrigé - augmenter la confiance légèrement
        # mais aussi ajouter le message aux exemples
        matching_rules = engine.find_matching_rules(message)
        for rule in matching_rules:
            if rule["action"] == corrected_action:
                rule["confidence"] = min(1.0, rule["confidence"] + 0.02)
                if message not in rule["examples"]:
                    rule["examples"].append(message)
        
        # Ajouter à l'historique des annotations
        if "annotated_messages" not in annotator.annotations:
            annotator.annotations["annotated_messages"] = []
        
        annotator.annotations["annotated_messages"].append({
            "message": message,
            "action": corrected_action,
            "target_type": corrected_type,
            "identifier": corrected_id,
            "confidence": feedback_entry.get("confidence", 0.5)
        })
    
    elif verdict == "wrong":
        # Le modèle était complètement faux - ne pas l'entraîner
        pass

if __name__ == "__main__":
    main()
