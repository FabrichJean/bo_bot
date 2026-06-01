"""
Tests du système d'annotation de données chinoises.
"""

from data_annotator import DataAnnotator
import json
import os


def test_data_annotator():
    """Teste la classe DataAnnotator."""
    print("=" * 60)
    print("🧪 TEST: Système d'Annotation")
    print("=" * 60)
    
    # Créer une instance
    annotator = DataAnnotator(data_file='test_annotations.json')
    
    # Test 1: Ajouter des messages
    print("\n1️⃣ TEST: Ajouter des messages en chinois")
    messages = [
        "启用 Wangpai 平台",
        "关闭 jincheng 频道",
        "激活 ID:156 平台",
        "禁用 Jincheng 频道",
    ]
    
    message_ids = []
    for msg in messages:
        msg_id = annotator.add_message(msg)
        message_ids.append(msg_id)
        print(f"   ✅ Ajouté: {msg_id} -> {msg}")
    
    # Test 2: Annoter les messages
    print("\n2️⃣ TEST: Annoter les messages")
    
    # Message 1: activate platform
    success = annotator.annotate_message(
        message_ids[0],
        action="activate",
        target_type="platform",
        identifier="Wangpai",
        confidence=0.95
    )
    print(f"   ✅ Annoté (activate/platform/Wangpai): {success}")
    
    # Message 2: deactivate channel
    success = annotator.annotate_message(
        message_ids[1],
        action="deactivate",
        target_type="channel",
        identifier="jincheng",
        confidence=0.90
    )
    print(f"   ✅ Annoté (deactivate/channel/jincheng): {success}")
    
    # Message 3: activate platform
    success = annotator.annotate_message(
        message_ids[2],
        action="activate",
        target_type="platform",
        identifier="156",
        confidence=0.85
    )
    print(f"   ✅ Annoté (activate/platform/156): {success}")
    
    # Message 4: marquer comme invalide
    annotator.mark_invalid(message_ids[3], reason="Syntaxe incorrecte")
    print(f"   ✅ Marqué comme invalide: {message_ids[3]}")
    
    # Test 3: Récupérer les statistiques
    print("\n3️⃣ TEST: Statistiques")
    stats = annotator.get_stats()
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Annotés: {stats['annotated']}")
    print(f"   À annoter: {stats['unannotated']}")
    print(f"   Progression: {stats['progress_percent']}%")
    print(f"   Par action: {stats['stats']['by_action']}")
    print(f"   Par type: {stats['stats']['by_target_type']}")
    print(f"   Par annotateur: {stats['stats']['by_annotator']}")
    
    # Test 4: Exporter les données d'entraînement
    print("\n4️⃣ TEST: Export des données")
    success = annotator.export_training_data('test_training_data.json')
    print(f"   ✅ Export réussi: {success}")
    
    if os.path.exists('test_training_data.json'):
        with open('test_training_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   📊 Samples exportés: {data['total_samples']}")
        print(f"   🎯 Premier sample:")
        if data['sentences']:
            first = data['sentences'][0]
            print(f"      Text: {first['text']}")
            print(f"      Action: {first['action']}")
            print(f"      Type: {first['target_type']}")
            print(f"      Identifiant: {first['identifier']}")
            print(f"      Confiance: {first['confidence']}")
            print(f"      Tokens: {first['tokens'][:5]}...")
    
    # Test 5: Tokenization
    print("\n5️⃣ TEST: Tokenization du chinois")
    test_texts = [
        "启用 Wangpai 平台",
        "关闭 ID:156 频道",
        "activate platform Wangpai"
    ]
    
    for text in test_texts:
        tokens = annotator._tokenize_chinese(text)
        print(f"   Text: {text}")
        print(f"   Tokens: {tokens}")
    
    # Test 6: Import depuis JSON
    print("\n6️⃣ TEST: Import depuis JSON")
    
    # Créer un fichier JSON de test
    test_json = [
        {"text": "打开 Wangpai"},
        {"text": "关闭 Jincheng"},
    ]
    
    with open('test_import.json', 'w', encoding='utf-8') as f:
        json.dump(test_json, f, ensure_ascii=False)
    
    # Importer
    annotator2 = DataAnnotator(data_file='test_annotations2.json')
    count = annotator2.import_from_json('test_import.json')
    print(f"   ✅ {count} messages importés")
    
    stats2 = annotator2.get_stats()
    print(f"   Total messages après import: {stats2['total_messages']}")
    
    # Nettoyage
    print("\n🧹 Nettoyage des fichiers de test...")
    for file in ['test_annotations.json', 'test_annotations2.json', 
                 'test_training_data.json', 'test_import.json']:
        if os.path.exists(file):
            os.remove(file)
            print(f"   ✅ Supprimé: {file}")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS RÉUSSIS!")
    print("=" * 60)


def test_sample_messages():
    """Teste avec les exemples de messages chinoises."""
    print("\n" + "=" * 60)
    print("🎯 TEST: Données d'Exemple Chinoises")
    print("=" * 60)
    
    # Charger les exemples
    with open('sample_messages_zh.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    print(f"\n📊 {len(messages)} messages d'exemple chargés")
    
    # Créer l'annotateur
    annotator = DataAnnotator(data_file='sample_annotations.json')
    
    # Importer les messages
    for msg in messages[:5]:  # Juste les 5 premiers
        annotator.add_message(msg['text'])
    
    print(f"✅ {5} messages ajoutés")
    
    # Afficher quelques messages
    print("\n📋 Exemples:")
    unannotated = annotator.get_unannotated_messages()
    for i, msg in enumerate(unannotated[:3], 1):
        print(f"   {i}. {msg['normalized_text']} (ID: {msg['id']})")
    
    # Nettoyage
    if os.path.exists('sample_annotations.json'):
        os.remove('sample_annotations.json')
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        test_data_annotator()
        test_sample_messages()
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
