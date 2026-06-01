"""
Script d'intégration du système d'annotation avec le RuleEngine.
Permet de charger les données annotées pour affiner les règles.
"""

import json
from data_annotator import DataAnnotator
from rule_engine import RuleEngine, MessageExtractor


def load_training_data_into_rules(training_file: str = 'training_data.json'):
    """
    Charge les données annotées et les utilise pour créer/améliorer les règles.
    
    Args:
        training_file: Fichier JSON avec les données d'entraînement
    
    Returns:
        Nombre de règles créées/mises à jour
    """
    print("=" * 70)
    print("🔄 Intégration Annotation → RuleEngine")
    print("=" * 70)
    
    # Charger le RuleEngine
    engine = RuleEngine()
    print(f"\n✅ RuleEngine chargé avec {len(engine.rules)} règles")
    
    # Charger les données d'entraînement
    try:
        with open(training_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {training_file}")
        print("   Exécutez d'abord: annotator.export_training_data()")
        return 0
    
    print(f"\n📊 {training_data['total_samples']} samples chargés")
    
    # Analyser les données
    print("\n" + "=" * 70)
    print("📈 ANALYSE DES DONNÉES D'ENTRAÎNEMENT")
    print("=" * 70)
    
    action_stats = {}
    type_stats = {}
    identifier_stats = {}
    
    for sample in training_data['sentences']:
        action = sample['action']
        target_type = sample['target_type']
        identifier = sample['identifier']
        
        action_stats[action] = action_stats.get(action, 0) + 1
        type_stats[target_type] = type_stats.get(target_type, 0) + 1
        identifier_stats[identifier] = identifier_stats.get(identifier, 0) + 1
    
    print("\n🎯 Par Action:")
    for action, count in sorted(action_stats.items()):
        percentage = (count / training_data['total_samples']) * 100
        print(f"   • {action}: {count} ({percentage:.1f}%)")
    
    print("\n🎪 Par Type:")
    for type_, count in sorted(type_stats.items()):
        percentage = (count / training_data['total_samples']) * 100
        print(f"   • {type_}: {count} ({percentage:.1f}%)")
    
    print("\n🏷️ Identifiants les plus courants:")
    sorted_ids = sorted(identifier_stats.items(), key=lambda x: x[1], reverse=True)
    for identifier, count in sorted_ids[:5]:
        print(f"   • {identifier}: {count}")
    
    # Améliorer les règles
    print("\n" + "=" * 70)
    print("🚀 AMÉLIORATION DES RÈGLES")
    print("=" * 70)
    
    updated_count = 0
    new_count = 0
    
    for sample in training_data['sentences']:
        action = sample['action']
        target_type = sample['target_type']
        identifier = sample['identifier']
        text = sample['text']
        
        # Chercher une règle existante
        matching_rules = engine.find_matching_rules(text)
        
        if matching_rules:
            # Améliorer la meilleure règle
            best_rule, best_confidence = matching_rules[0]  # C'est un tuple (rule, confidence)
            old_confidence = best_rule['confidence']
            
            # Ajouter l'exemple à la règle
            if 'examples' not in best_rule:
                best_rule['examples'] = []
            if text not in best_rule['examples']:
                best_rule['examples'].append(text)
            
            # Augmenter la confiance légèrement
            best_rule['confidence'] = min(1.0, best_rule['confidence'] + 0.02)
            
            print(f"✅ Amélioré: {best_rule['id']}")
            print(f"   Confiance: {old_confidence:.2f} → {best_rule['confidence']:.2f}")
            updated_count += 1
        else:
            # Créer une nouvelle règle si aucune ne match
            # (Cela arrive rarement si les règles par défaut sont bien définies)
            print(f"ℹ️  Pas de règle correspondante pour: {text}")
    
    # Sauvegarder les améliorations
    engine.save_rules()
    print(f"\n💾 Règles sauvegardées")
    
    # Afficher le résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 70)
    
    stats = engine.get_rules_stats()
    print(f"\n📈 Règles:")
    print(f"   Total: {len(engine.rules)}")
    print(f"   Améliorées: {updated_count}")
    print(f"   Créées: {new_count}")
    print(f"   Confiance moyenne: {stats['avg_confidence']:.2f}")
    print(f"   Confiance min: {stats['min_confidence']:.2f}")
    print(f"   Confiance max: {stats['max_confidence']:.2f}")
    
    print("\n" + "=" * 70)
    print(f"✅ INTÉGRATION TERMINÉE")
    print("=" * 70)
    
    return updated_count + new_count


def validate_annotation_quality(training_file: str = 'training_data.json') -> dict:
    """
    Valide la qualité des annotations pour l'entraînement.
    
    Args:
        training_file: Fichier JSON avec les données d'entraînement
    
    Returns:
        Dict avec les métriques de qualité
    """
    print("\n" + "=" * 70)
    print("🔍 VALIDATION DE LA QUALITÉ")
    print("=" * 70)
    
    try:
        with open(training_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {training_file}")
        return {}
    
    metrics = {
        'total_samples': training_data['total_samples'],
        'avg_confidence': 0,
        'min_confidence': 1.0,
        'max_confidence': 0.0,
        'samples_by_confidence': {},
        'missing_fields': 0,
        'recommendations': []
    }
    
    confidences = []
    
    for sample in training_data['sentences']:
        confidence = sample.get('confidence', 1.0)
        confidences.append(confidence)
        
        # Vérifier les champs obligatoires
        required_fields = ['text', 'action', 'target_type', 'identifier']
        for field in required_fields:
            if field not in sample or not sample[field]:
                metrics['missing_fields'] += 1
        
        # Binning par confiance
        conf_bin = int(confidence * 10) / 10  # 0.0, 0.1, 0.2, etc.
        metrics['samples_by_confidence'][conf_bin] = \
            metrics['samples_by_confidence'].get(conf_bin, 0) + 1
    
    # Calculer les statistiques
    if confidences:
        metrics['avg_confidence'] = sum(confidences) / len(confidences)
        metrics['min_confidence'] = min(confidences)
        metrics['max_confidence'] = max(confidences)
    
    # Recommandations
    print("\n📊 Métriques:")
    print(f"   Total samples: {metrics['total_samples']}")
    print(f"   Confiance moyenne: {metrics['avg_confidence']:.2f}")
    print(f"   Confiance min: {metrics['min_confidence']:.2f}")
    print(f"   Confiance max: {metrics['max_confidence']:.2f}")
    print(f"   Champs manquants: {metrics['missing_fields']}")
    
    print("\n📈 Distribution par confiance:")
    for conf, count in sorted(metrics['samples_by_confidence'].items()):
        percentage = (count / metrics['total_samples']) * 100
        bar = "█" * int(percentage / 5)
        print(f"   {conf:.1f}-{conf+0.1:.1f}: {bar} {count} ({percentage:.1f}%)")
    
    # Générer les recommandations
    if metrics['avg_confidence'] < 0.90:
        metrics['recommendations'].append(
            "⚠️  Confiance moyenne faible (<0.90). "
            "Revérifiez les annotations ambiguës."
        )
    
    if metrics['missing_fields'] > 0:
        metrics['recommendations'].append(
            f"⚠️  {metrics['missing_fields']} champs manquants. "
            "Compléter les données incomplètes."
        )
    
    if metrics['total_samples'] < 20:
        metrics['recommendations'].append(
            "ℹ️  Peu de samples (<20). Ajouter plus de données d'entraînement."
        )
    
    if metrics['total_samples'] >= 100 and metrics['avg_confidence'] >= 0.95:
        metrics['recommendations'].append(
            "✅ Excellent! Les données sont prêtes pour entraîner le modèle."
        )
    
    if metrics['recommendations']:
        print("\n💡 Recommandations:")
        for rec in metrics['recommendations']:
            print(f"   {rec}")
    
    return metrics


def create_training_splits(training_file: str = 'training_data.json',
                          train_ratio: float = 0.8) -> tuple:
    """
    Crée des splits train/test pour l'entraînement du modèle.
    
    Args:
        training_file: Fichier avec les données
        train_ratio: Ratio train (ex: 0.8 = 80% train, 20% test)
    
    Returns:
        Tuple (train_data, test_data)
    """
    try:
        with open(training_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {training_file}")
        return None, None
    
    sentences = training_data['sentences']
    split_idx = int(len(sentences) * train_ratio)
    
    train_data = {
        'version': training_data['version'],
        'export_date': training_data['export_date'],
        'total_samples': split_idx,
        'sentences': sentences[:split_idx]
    }
    
    test_data = {
        'version': training_data['version'],
        'export_date': training_data['export_date'],
        'total_samples': len(sentences) - split_idx,
        'sentences': sentences[split_idx:]
    }
    
    # Sauvegarder
    with open('training_data_train.json', 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open('training_data_test.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("✂️  CRÉATION DES SPLITS")
    print("=" * 70)
    print(f"\n✅ Train: {split_idx} samples → training_data_train.json")
    print(f"✅ Test: {len(sentences) - split_idx} samples → training_data_test.json")
    
    return train_data, test_data


if __name__ == "__main__":
    print("""
    🔄 Script d'Intégration Annotation → RuleEngine
    ===============================================
    
    Choisissez une action:
    1. Intégrer les données annotées
    2. Valider la qualité
    3. Créer splits train/test
    4. Tout faire
    """)
    
    choice = input("\n> Votre choix (1-4): ").strip()
    
    if choice in ['1', '4']:
        load_training_data_into_rules()
    
    if choice in ['2', '4']:
        validate_annotation_quality()
    
    if choice in ['3', '4']:
        create_training_splits()
    
    print("\n✅ Terminé!\n")
