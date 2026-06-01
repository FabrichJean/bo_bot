"""
Interface de Test et Feedback pour le Modèle
Permet de tester le modèle sur de nouveaux messages et nourrir le système avec les corrections.
"""

from flask import Flask, render_template, request, jsonify
from rule_engine import RuleEngine, MessageExtractor
from data_annotator import DataAnnotator
import json
import os
from datetime import datetime


app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialiser le moteur et l'annotateur
engine = RuleEngine()
annotator = DataAnnotator(data_file='test_feedback.json')

# Suivi des tests en cours
pending_tests = {}  # message_id -> test_result


# ============= ROUTES PRINCIPALES =============

@app.route('/test')
def test_interface():
    """Page principale de test."""
    stats = engine.get_rules_stats()
    return render_template('test.html', stats=stats)


@app.route('/test/results')
def test_results():
    """Page des résultats de test."""
    # Récupérer les feedback stockés
    feedback_data = annotator.annotations.get("feedback", [])
    
    # Grouper par statut
    correct = sum(1 for f in feedback_data if f.get('user_verdict') == 'correct')
    corrected = sum(1 for f in feedback_data if f.get('user_verdict') == 'corrected')
    wrong = sum(1 for f in feedback_data if f.get('user_verdict') == 'wrong')
    
    return render_template('test_results.html',
                         total=len(feedback_data),
                         correct=correct,
                         corrected=corrected,
                         wrong=wrong,
                         accuracy=round(correct / len(feedback_data) * 100) if feedback_data else 0)


@app.route('/test/history')
def test_history():
    """Historique des tests."""
    feedback_data = annotator.annotations.get("feedback", [])
    # Limiter aux 50 derniers
    feedback_data = sorted(feedback_data, 
                          key=lambda x: x.get('timestamp', ''), 
                          reverse=True)[:50]
    
    return render_template('test_history.html', feedback=feedback_data)


# ============= API ENDPOINTS =============

@app.route('/api/test/predict', methods=['POST'])
def predict():
    """
    Teste le modèle sur un message.
    Retourne la prédiction du modèle.
    """
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'error': 'Message vide'}), 400
    
    # Extraire les composants
    components = MessageExtractor.extract_components(message)
    
    # Trouver la meilleure règle
    best_match = engine.find_best_match(message)
    
    # Préparer le résultat
    result = {
        'message': message,
        'model_prediction': {
            'action': components['action'],
            'target_type': components['target_type'],
            'identifier': components['identifier']
        },
        'matched_rule': None,
        'confidence': 0.0,
        'timestamp': datetime.now().isoformat()
    }
    
    test_id = None
    if best_match:
        rule, confidence = best_match
        result['matched_rule'] = {
            'id': rule['id'],
            'pattern': rule.get('pattern', ''),
            'confidence': confidence
        }
        result['confidence'] = confidence
        
        # Générer un test_id temporaire
        test_id = f"test_{len(pending_tests) + 1:05d}"
        pending_tests[test_id] = result
    
    return jsonify({'success': True, 'result': result, 'test_id': test_id})


@app.route('/api/test/feedback', methods=['POST'])
def submit_feedback():
    """
    Soumet un feedback sur la prédiction du modèle.
    Nourrit le système avec les corrections.
    """
    data = request.get_json()
    
    message = data.get('message', '')
    user_verdict = data.get('verdict', '')  # correct, corrected, wrong
    corrected_action = data.get('action')
    corrected_type = data.get('target_type')
    corrected_identifier = data.get('identifier')
    confidence = data.get('confidence', 1.0)
    
    if not all([message, user_verdict]):
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400
    
    # Valider le verdict
    valid_verdicts = ['correct', 'corrected', 'wrong']
    if user_verdict not in valid_verdicts:
        return jsonify({'success': False, 'error': 'Verdict invalide'}), 400
    
    # Enregistrer le feedback
    feedback_entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'user_verdict': user_verdict,  # correct, corrected, wrong
        'corrected_action': corrected_action,
        'corrected_target_type': corrected_type,
        'corrected_identifier': corrected_identifier,
        'confidence': confidence
    }
    
    # Initialiser feedback si nécessaire
    if 'feedback' not in annotator.annotations:
        annotator.annotations['feedback'] = []
    
    annotator.annotations['feedback'].append(feedback_entry)
    
    # Si feedback corrigé, l'ajouter à l'annotateur
    if user_verdict in ['correct', 'corrected']:
        # Déterminer l'action finale
        if user_verdict == 'correct':
            # Utiliser la prédiction du modèle
            components = MessageExtractor.extract_components(message)
            final_action = components['action']
            final_type = components['target_type']
            final_identifier = components['identifier']
        else:
            # Utiliser la correction de l'utilisateur
            final_action = corrected_action
            final_type = corrected_type
            final_identifier = corrected_identifier
        
        # Ajouter comme message annoté
        msg_id = annotator.add_message(message, source='test_feedback')
        annotator.annotate_message(
            msg_id,
            action=final_action,
            target_type=final_type,
            identifier=final_identifier,
            confidence=confidence,
            annotator='test_feedback'
        )
    
    # Sauvegarder
    annotator._save_annotations()
    
    # Réentraîner le modèle avec ce feedback
    _train_model_with_feedback(feedback_entry)
    
    return jsonify({
        'success': True,
        'feedback_recorded': True,
        'stats': _get_test_stats()
    })


@app.route('/api/test/batch', methods=['POST'])
def batch_test():
    """
    Teste le modèle sur plusieurs messages.
    Accepte un JSON avec une liste de messages.
    """
    data = request.get_json()
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({'success': False, 'error': 'Pas de messages'}), 400
    
    results = []
    for msg in messages:
        components = MessageExtractor.extract_components(msg)
        best_match = engine.find_best_match(msg)
        
        result = {
            'message': msg,
            'prediction': {
                'action': components['action'],
                'target_type': components['target_type'],
                'identifier': components['identifier']
            },
            'confidence': best_match[1] if best_match else 0.0
        }
        results.append(result)
    
    return jsonify({
        'success': True,
        'results': results,
        'total': len(results)
    })


@app.route('/api/test/stats', methods=['GET'])
def get_test_stats():
    """Récupère les statistiques de test."""
    return jsonify(_get_test_stats())


@app.route('/api/test/export', methods=['GET'])
def export_test_results():
    """Exporte les résultats de test."""
    feedback_data = annotator.annotations.get("feedback", [])
    
    export_data = {
        'version': '1.0',
        'export_date': datetime.now().isoformat(),
        'total_tests': len(feedback_data),
        'feedback': feedback_data
    }
    
    filename = f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'total_tests': len(feedback_data)
    })


@app.route('/api/test/clear', methods=['POST'])
def clear_tests():
    """Efface l'historique des tests."""
    if 'feedback' in annotator.annotations:
        del annotator.annotations['feedback']
    annotator._save_annotations()
    pending_tests.clear()
    
    return jsonify({'success': True, 'message': 'Historique effacé'})


# ============= FONCTIONS UTILITAIRES =============

def _get_test_stats() -> dict:
    """Récupère les statistiques de test."""
    feedback_data = annotator.annotations.get("feedback", [])
    
    if not feedback_data:
        return {
            'total_tests': 0,
            'correct': 0,
            'corrected': 0,
            'wrong': 0,
            'accuracy_percent': 0,
            'feedback_used_for_training': 0
        }
    
    correct = sum(1 for f in feedback_data if f.get('user_verdict') == 'correct')
    corrected = sum(1 for f in feedback_data if f.get('user_verdict') == 'corrected')
    wrong = sum(1 for f in feedback_data if f.get('user_verdict') == 'wrong')
    
    # Compter les utilisés pour l'entraînement
    training_used = correct + corrected
    
    return {
        'total_tests': len(feedback_data),
        'correct': correct,
        'corrected': corrected,
        'wrong': wrong,
        'accuracy_percent': round((correct + corrected) / len(feedback_data) * 100) if feedback_data else 0,
        'feedback_used_for_training': training_used
    }


def _train_model_with_feedback(feedback_entry: dict):
    """
    Réentraîne le modèle avec le feedback.
    Améliore les règles existantes ou en crée de nouvelles.
    """
    message = feedback_entry['message']
    user_verdict = feedback_entry['user_verdict']
    
    if user_verdict == 'wrong':
        # Si complètement faux, ne rien faire (ou pénaliser)
        return
    
    # Déterminer l'action correcte
    if user_verdict == 'correct':
        components = MessageExtractor.extract_components(message)
        action = components['action']
        target_type = components['target_type']
    else:
        action = feedback_entry['corrected_action']
        target_type = feedback_entry['corrected_target_type']
    
    # Trouver la règle correspondante
    matching_rules = engine.find_matching_rules(message)
    
    if matching_rules:
        # Améliorer la meilleure règle
        best_rule, conf = matching_rules[0]
        
        # Ajouter l'exemple
        if 'examples' not in best_rule:
            best_rule['examples'] = []
        if message not in best_rule['examples']:
            best_rule['examples'].append(message)
        
        # Augmenter confiance si verdict positif
        if user_verdict == 'correct':
            best_rule['confidence'] = min(1.0, best_rule['confidence'] + 0.03)
        elif user_verdict == 'corrected':
            best_rule['confidence'] = min(1.0, best_rule['confidence'] + 0.02)
    
    # Sauvegarder
    engine.save_rules()


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    🧪 Interface de Test et Feedback
    ================================
    
    Ouvrez: http://localhost:5001
    
    Routes:
    • /test           - Interface de test
    • /test/results   - Résultats
    • /test/history   - Historique
    
    La page de test permet:
    ✓ Tester le modèle
    ✓ Valider/corriger les prédictions
    ✓ Nourrir le système avec le feedback
    ✓ Améliorer le modèle automatiquement
    
    Appuyez sur Ctrl+C pour arrêter
    """)
    
    app.run(debug=True, port=5001)
