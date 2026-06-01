"""
Test du système Rule Engine + Message Processor.
Démontre le fonctionnement du système d'apprentissage.
"""

import asyncio
from rule_engine import get_rule_engine, MessageExtractor
from message_processor import MessageProcessor


def test_message_extractor():
    """Test l'extraction des composants."""
    print("\n" + "="*70)
    print("📋 TEST: Message Extractor")
    print("="*70)
    
    test_messages = [
        "activate platform Wangpai",
        "deactivate channel 156",
        "turn on the Wangpai platform",
        "disable channel ID:156",
        "enable platform Jincheng",
        "turn off channel ID:8",
    ]
    
    for message in test_messages:
        components = MessageExtractor.extract_components(message)
        print(f"\n📝 Message: '{message}'")
        print(f"  → Action: {components['action']}")
        print(f"  → Type: {components['target_type']}")
        print(f"  → ID: {components['identifier']}")


def test_rule_matching():
    """Test le matching des règles."""
    print("\n" + "="*70)
    print("🎯 TEST: Rule Matching & Confidence Scoring")
    print("="*70)
    
    engine = get_rule_engine()
    
    test_messages = [
        "activate platform Wangpai",
        "turn on the platform Wangpai",
        "activate Wangpai",  # Confiance plus basse
        "deactivate channel 156",
        "disable the channel ID:156",
        "hey how is the platform",  # Très basse confiance
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        
        matches = engine.find_matching_rules(message)
        
        if matches:
            for rule, confidence in matches[:3]:  # Top 3
                print(f"  • Règle: '{rule['id']}'")
                print(f"    Confiance: {confidence:.1%}")
                print(f"    Action: {rule['action']}")
        else:
            print("  ❌ Aucune règle correspondante")


def test_learning_system():
    """Test le système d'apprentissage."""
    print("\n" + "="*70)
    print("🧠 TEST: Learning System")
    print("="*70)
    
    engine = get_rule_engine()
    
    print("\n📊 État initial:")
    stats = engine.get_rules_stats()
    print(f"  • Règles: {stats['total_rules']}")
    print(f"  • Historique: {stats['total_history']}")
    print(f"  • Confiance moyenne: {stats['average_confidence']:.1%}")
    
    # Simuler une validation
    message = "activate platform Wangpai"
    print(f"\n✅ Validé: '{message}'")
    
    before = engine.rules[0]['confidence']
    engine.add_learned_message(
        message=message,
        action="activate",
        target_type="platform",
        identifier="Wangpai",
        sender="admin",
        status="success"
    )
    after = engine.rules[0]['confidence']
    
    print(f"  • Confiance avant: {before:.1%}")
    print(f"  • Confiance après: {after:.1%}")
    print(f"  • Augmentation: +{(after-before):.1%}")
    
    print("\n📊 État final:")
    stats = engine.get_rules_stats()
    print(f"  • Règles: {stats['total_rules']}")
    print(f"  • Historique: {stats['total_history']}")
    print(f"  • Confiance moyenne: {stats['average_confidence']:.1%}")


async def test_message_processor():
    """Test le processeur de messages."""
    print("\n" + "="*70)
    print("🔄 TEST: Message Processor")
    print("="*70)
    
    processor = MessageProcessor()
    
    test_cases = [
        {
            "message": "activate platform Wangpai",
            "sender": "admin",
            "description": "Message standard avec haute confiance"
        },
        {
            "message": "turn on the Wangpai platform",
            "sender": "admin",
            "description": "Message avec variante (confiance moyenne)"
        },
        {
            "message": "how is the platform doing",
            "sender": "user",
            "description": "Message non pertinent"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n Test {i}: {test['description']}")
        print(f"  📝 Message: '{test['message']}'")
        print(f"  👤 Sender: {test['sender']}")
        
        result = await processor.process_message(
            message=test['message'],
            sender=test['sender'],
            message_id=i
        )
        
        print(f"\n  Résultat:")
        print(f"    • Processed: {result['processed']}")
        print(f"    • Confiance: {result['confidence']:.1%}")
        print(f"    • Status: {result['status']}")
        if result['response']:
            print(f"    • Response:\n      {result['response']}")


def test_rules_details():
    """Affiche les détails de toutes les règles."""
    print("\n" + "="*70)
    print("📚 TEST: Règles Détaillées")
    print("="*70)
    
    engine = get_rule_engine()
    
    for rule in engine.rules:
        print(f"\n📌 Règle: {rule['id']}")
        print(f"  • Confiance: {rule['confidence']:.1%}")
        print(f"  • Validations: {rule.get('validation_count', 0)}")
        print(f"  • Keywords: {', '.join(rule.get('keywords', []))}")
        print(f"  • Exemples: {rule.get('examples', [])[:3]}")


async def main():
    """Lance tous les tests."""
    print("\n🚀 TESTS DU SYSTÈME D'APPRENTISSAGE\n")
    
    test_message_extractor()
    test_rule_matching()
    test_learning_system()
    await test_message_processor()
    test_rules_details()
    
    print("\n" + "="*70)
    print("✅ TOUS LES TESTS COMPLÉTÉS")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
