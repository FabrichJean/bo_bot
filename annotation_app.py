"""
Application Flask pour annoter les messages en chinois.
Interface web légère pour annoter, corriger et exporter les données.
"""

from flask import Flask, render_template, request, jsonify, send_file
from data_annotator import DataAnnotator
import json
import os
from datetime import datetime


app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialiser l'annotateur
annotator = DataAnnotator()


# ============= ROUTES PRINCIPALES =============

@app.route('/')
def index():
    """Page d'accueil avec upload."""
    stats = annotator.get_stats()
    return render_template('index.html', stats=stats)


@app.route('/annotate')
def annotate():
    """Page d'annotation."""
    unannotated = annotator.get_unannotated_messages()
    
    if not unannotated:
        return render_template('annotate.html', 
                             message=None, 
                             total=0, 
                             current=0,
                             finished=True)
    
    current_msg = unannotated[0]
    stats = annotator.get_stats()
    
    return render_template('annotate.html',
                         message=current_msg,
                         total=stats['total_messages'],
                         current=stats['annotated'] + 1,
                         finished=False)


@app.route('/stats')
def stats():
    """Page des statistiques."""
    stats = annotator.get_stats()
    
    # Récupérer les messages annotés pour afficher les exemples
    annotated = annotator.get_annotated_messages()
    
    return render_template('stats.html', 
                         stats=stats,
                         annotated_count=len(annotated))


# ============= API ENDPOINTS =============

@app.route('/api/messages/unannotated', methods=['GET'])
def get_unannotated():
    """Retourne les messages non annotés."""
    unannotated = annotator.get_unannotated_messages()
    return jsonify({
        'count': len(unannotated),
        'messages': unannotated[:10]  # Limiter à 10
    })


@app.route('/api/messages/<message_id>', methods=['GET'])
def get_message(message_id):
    """Retourne un message spécifique."""
    msg = annotator.get_message(message_id)
    if msg:
        return jsonify({'success': True, 'message': msg})
    return jsonify({'success': False, 'error': 'Message not found'}), 404


@app.route('/api/annotate', methods=['POST'])
def submit_annotation():
    """Reçoit une annotation."""
    data = request.get_json()
    
    message_id = data.get('message_id')
    action = data.get('action')
    target_type = data.get('target_type')
    identifier = data.get('identifier')
    confidence = data.get('confidence', 1.0)
    annotator_name = data.get('annotator', 'web-ui')
    
    # Valider
    if not all([message_id, action, target_type, identifier]):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    try:
        confidence = float(confidence)
        if not (0.0 <= confidence <= 1.0):
            confidence = 1.0
    except:
        confidence = 1.0
    
    # Annoter
    success = annotator.annotate_message(
        message_id,
        action=action,
        target_type=target_type,
        identifier=identifier,
        confidence=confidence,
        annotator=annotator_name
    )
    
    if success:
        # Récupérer le prochain message
        unannotated = annotator.get_unannotated_messages()
        next_msg = unannotated[0] if unannotated else None
        
        return jsonify({
            'success': True,
            'next_message': next_msg,
            'remaining': len(unannotated)
        })
    
    return jsonify({'success': False, 'error': 'Could not annotate'}), 500


@app.route('/api/invalid', methods=['POST'])
def mark_invalid():
    """Marque un message comme invalide."""
    data = request.get_json()
    
    message_id = data.get('message_id')
    reason = data.get('reason', 'Invalid format')
    annotator_name = data.get('annotator', 'web-ui')
    
    success = annotator.mark_invalid(message_id, reason, annotator_name)
    
    if success:
        unannotated = annotator.get_unannotated_messages()
        next_msg = unannotated[0] if unannotated else None
        
        return jsonify({
            'success': True,
            'next_message': next_msg,
            'remaining': len(unannotated)
        })
    
    return jsonify({'success': False, 'error': 'Could not mark invalid'}), 500


@app.route('/api/upload/json', methods=['POST'])
def upload_json():
    """Importe des messages depuis un JSON."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'success': False, 'error': 'Must be JSON'}), 400
    
    try:
        # Sauvegarder temporairement et importer
        temp_path = '/tmp/upload.json'
        file.save(temp_path)
        
        count = annotator.import_from_json(temp_path)
        os.remove(temp_path)
        
        stats = annotator.get_stats()
        
        return jsonify({
            'success': True,
            'imported': count,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload/csv', methods=['POST'])
def upload_csv():
    """Importe des messages depuis un CSV."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Must be CSV'}), 400
    
    try:
        temp_path = '/tmp/upload.csv'
        file.save(temp_path)
        
        column = request.form.get('column', '0')
        try:
            column = int(column)
        except:
            column = 0
        
        count = annotator.import_from_csv(temp_path, column)
        os.remove(temp_path)
        
        stats = annotator.get_stats()
        
        return jsonify({
            'success': True,
            'imported': count,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/add-message', methods=['POST'])
def add_message():
    """Ajoute un message manuellement."""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'error': 'Empty text'}), 400
    
    msg_id = annotator.add_message(text, source='manual')
    
    return jsonify({
        'success': True,
        'message_id': msg_id,
        'stats': annotator.get_stats()
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques."""
    return jsonify(annotator.get_stats())


@app.route('/api/export', methods=['GET'])
def export_data():
    """Exporte les données annotées."""
    output_file = 'training_data.json'
    annotator.export_training_data(output_file)
    
    if os.path.exists(output_file):
        return send_file(
            output_file,
            as_attachment=True,
            download_name=f'training_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    
    return jsonify({'success': False, 'error': 'Export failed'}), 500


@app.route('/api/export/raw', methods=['GET'])
def export_raw():
    """Exporte les annotations brutes."""
    output_file = f'annotated_messages_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(annotator.annotations, f, ensure_ascii=False, indent=2)
    
    return send_file(
        output_file,
        as_attachment=True,
        download_name=output_file
    )


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    🎯 Système d'Annotation de Données
    ===================================
    
    Ouvrez votre navigateur: http://localhost:5000
    
    Fonctionnalités:
    • Upload JSON/CSV
    • Annotation interactive
    • Statistiques en temps réel
    • Export pour entraînement
    
    Appuyez sur Ctrl+C pour arrêter
    """)
    
    app.run(debug=True, port=5000)
