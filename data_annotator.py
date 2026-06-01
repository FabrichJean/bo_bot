"""
Système d'annotation de données pour entraîner le modèle sur le chinois.
Supporte le chinois simplifié et traditionnel.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path
import re

# Conversion Chinois Simplifié <-> Traditionnel (optionnel)
try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None


class DataAnnotator:
    """Gère l'annotation de messages en chinois."""
    
    def __init__(self, data_file: str = "annotated_messages.json", 
                 simplified_only: bool = True):
        """
        Initialise l'annotateur.
        
        Args:
            data_file: Fichier pour sauvegarder les annotations
            simplified_only: Si True, convertir en chinois simplifié
        """
        self.data_file = data_file
        self.simplified_only = simplified_only
        
        # Convertisseur Traditionnel -> Simplifié
        self.cc = None
        if simplified_only and OpenCC is not None:
            self.cc = OpenCC('t2s')
        
        # Charger les données existantes
        self.annotations = self._load_annotations()
    
    def _load_annotations(self) -> Dict:
        """Charge les annotations depuis le fichier."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Erreur lors du chargement: {e}")
                return self._create_empty_database()
        return self._create_empty_database()
    
    def _create_empty_database(self) -> Dict:
        """Crée une base de données vide."""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "total_annotations": 0,
            "messages": [],
            "stats": {
                "by_action": {},
                "by_target_type": {},
                "by_annotator": {}
            }
        }
    
    def _save_annotations(self):
        """Sauvegarde les annotations dans le fichier."""
        self.annotations["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.annotations, f, ensure_ascii=False, indent=2)
    
    def _normalize_chinese(self, text: str) -> str:
        """Normalise le texte chinois."""
        if self.cc:
            text = self.cc.convert(text)
        # Supprimer les espaces inutiles
        text = text.strip()
        return text
    
    def add_message(self, original_text: str, source: str = "telegram") -> str:
        """
        Ajoute un nouveau message à annoter.
        
        Args:
            original_text: Le message original en chinois
            source: Source du message (telegram, csv, etc.)
        
        Returns:
            message_id du message ajouté
        """
        normalized = self._normalize_chinese(original_text)
        
        # Vérifier si le message existe déjà
        for msg in self.annotations["messages"]:
            if msg["normalized_text"] == normalized:
                return msg["id"]
        
        # Créer un nouvel ID
        message_id = f"msg_{len(self.annotations['messages']) + 1:05d}"
        
        message = {
            "id": message_id,
            "original_text": original_text,
            "normalized_text": normalized,
            "source": source,
            "added_at": datetime.now().isoformat(),
            "annotation": None,  # Sera rempli pendant l'annotation
            "annotator": None,
            "annotation_date": None,
            "confidence": None
        }
        
        self.annotations["messages"].append(message)
        self._save_annotations()
        
        return message_id
    
    def annotate_message(self, message_id: str, 
                        action: str,  # activate/deactivate
                        target_type: str,  # platform/channel
                        identifier: str,  # nom/ID
                        confidence: float = 1.0,
                        annotator: str = "admin") -> bool:
        """
        Annote un message avec les détails détectés.
        
        Args:
            message_id: ID du message
            action: activate ou deactivate
            target_type: platform ou channel
            identifier: nom ou ID (ex: Wangpai, 156)
            confidence: 0.0 à 1.0 (confiance de l'annotateur)
            annotator: Qui a annoté
        
        Returns:
            True si succès
        """
        # Valider les entrées
        valid_actions = ["activate", "deactivate"]
        valid_types = ["platform", "channel"]
        
        if action not in valid_actions:
            print(f"❌ Action invalide: {action}. Doit être: {valid_actions}")
            return False
        
        if target_type not in valid_types:
            print(f"❌ Type invalide: {target_type}. Doit être: {valid_types}")
            return False
        
        # Trouver le message
        for msg in self.annotations["messages"]:
            if msg["id"] == message_id:
                msg["annotation"] = {
                    "action": action,
                    "target_type": target_type,
                    "identifier": identifier
                }
                msg["annotator"] = annotator
                msg["annotation_date"] = datetime.now().isoformat()
                msg["confidence"] = confidence
                
                self.annotations["total_annotations"] += 1
                self._update_stats(action, target_type, annotator)
                self._save_annotations()
                return True
        
        print(f"❌ Message non trouvé: {message_id}")
        return False
    
    def mark_invalid(self, message_id: str, reason: str = "Format invalide",
                    annotator: str = "admin") -> bool:
        """
        Marque un message comme invalide (ne peut pas être annoté).
        
        Args:
            message_id: ID du message
            reason: Raison de l'invalidation
            annotator: Qui a invalidé
        
        Returns:
            True si succès
        """
        for msg in self.annotations["messages"]:
            if msg["id"] == message_id:
                msg["annotation"] = {
                    "action": None,
                    "target_type": None,
                    "identifier": None,
                    "invalid": True,
                    "reason": reason
                }
                msg["annotator"] = annotator
                msg["annotation_date"] = datetime.now().isoformat()
                msg["confidence"] = 0.0
                self._save_annotations()
                return True
        
        return False
    
    def _update_stats(self, action: str, target_type: str, annotator: str):
        """Met à jour les statistiques."""
        # Par action
        if action not in self.annotations["stats"]["by_action"]:
            self.annotations["stats"]["by_action"][action] = 0
        self.annotations["stats"]["by_action"][action] += 1
        
        # Par type
        if target_type not in self.annotations["stats"]["by_target_type"]:
            self.annotations["stats"]["by_target_type"][target_type] = 0
        self.annotations["stats"]["by_target_type"][target_type] += 1
        
        # Par annotateur
        if annotator not in self.annotations["stats"]["by_annotator"]:
            self.annotations["stats"]["by_annotator"][annotator] = 0
        self.annotations["stats"]["by_annotator"][annotator] += 1
    
    def get_unannotated_messages(self) -> List[Dict]:
        """Récupère les messages non annotés."""
        return [msg for msg in self.annotations["messages"] 
                if msg["annotation"] is None]
    
    def get_annotated_messages(self) -> List[Dict]:
        """Récupère les messages annotés."""
        return [msg for msg in self.annotations["messages"] 
                if msg["annotation"] is not None and 
                not msg["annotation"].get("invalid")]
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Récupère un message par ID."""
        for msg in self.annotations["messages"]:
            if msg["id"] == message_id:
                return msg
        return None
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques d'annotation."""
        total = len(self.annotations["messages"])
        annotated = len(self.get_annotated_messages())
        unannotated = len(self.get_unannotated_messages())
        
        return {
            "total_messages": total,
            "annotated": annotated,
            "unannotated": unannotated,
            "progress_percent": round((annotated / total * 100) if total > 0 else 0, 2),
            "stats": self.annotations["stats"]
        }
    
    def export_training_data(self, output_file: str = "training_data.json") -> bool:
        """
        Exporte les données annotées pour entraîner le modèle.
        
        Format:
        {
            "sentences": [
                {
                    "text": "激活 Wangpai 平台",
                    "tokens": ["激活", "Wangpai", "平台"],
                    "action": "activate",
                    "target_type": "platform",
                    "identifier": "Wangpai"
                }
            ]
        }
        """
        annotated = self.get_annotated_messages()
        
        training_data = {
            "version": "1.0",
            "export_date": datetime.now().isoformat(),
            "total_samples": len(annotated),
            "sentences": []
        }
        
        for msg in annotated:
            if msg["annotation"] and not msg["annotation"].get("invalid"):
                sample = {
                    "id": msg["id"],
                    "text": msg["normalized_text"],
                    "original_text": msg["original_text"],
                    "tokens": self._tokenize_chinese(msg["normalized_text"]),
                    "action": msg["annotation"]["action"],
                    "target_type": msg["annotation"]["target_type"],
                    "identifier": msg["annotation"]["identifier"],
                    "confidence": msg["confidence"],
                    "annotator": msg["annotator"]
                }
                training_data["sentences"].append(sample)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Données exportées dans {output_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'export: {e}")
            return False
    
    def _tokenize_chinese(self, text: str) -> List[str]:
        """
        Tokenize un texte chinois.
        Utilise une approche simple: caractère par caractère pour le chinois,
        mots entiers pour l'anglais/nombres.
        """
        tokens = []
        current_token = ""
        
        for char in text:
            if self._is_chinese(char):
                # Ajouter le token anglais précédent s'il existe
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                # Ajouter le caractère chinois
                tokens.append(char)
            else:
                # Accumuler les caractères non-chinois
                current_token += char
        
        # Ajouter le dernier token
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _is_chinese(self, char: str) -> bool:
        """Vérifie si un caractère est chinois."""
        code = ord(char)
        # Les caractères chinois Unicode sont dans les plages:
        # CJK Unified Ideographs: 4E00-9FFF
        # CJK Unified Ideographs Extension A: 3400-4DBF
        return (0x4E00 <= code <= 0x9FFF or 
                0x3400 <= code <= 0x4DBF or
                0x20000 <= code <= 0x2A6DF or
                0x2A700 <= code <= 0x2B73F)
    
    def import_from_json(self, json_file: str) -> int:
        """
        Importe des messages depuis un fichier JSON.
        Format attendu: [{"text": "..."}, ...]
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "text" in item:
                        self.add_message(item["text"], source="import")
                        count += 1
                    elif isinstance(item, str):
                        self.add_message(item, source="import")
                        count += 1
            
            print(f"✅ {count} messages importés")
            return count
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
            return 0
    
    def import_from_csv(self, csv_file: str, text_column: int = 0) -> int:
        """
        Importe des messages depuis un CSV.
        
        Args:
            csv_file: Fichier CSV
            text_column: Index de la colonne contenant le texte
        """
        try:
            import csv
            count = 0
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > text_column:
                        self.add_message(row[text_column], source="csv")
                        count += 1
            
            print(f"✅ {count} messages importés depuis CSV")
            return count
        except Exception as e:
            print(f"❌ Erreur lors de l'import CSV: {e}")
            return 0


# ============= EXEMPLE D'UTILISATION =============
if __name__ == "__main__":
    annotator = DataAnnotator()
    
    # Ajouter quelques messages de test
    messages = [
        "启用 Wangpai 平台",
        "关闭 jincheng 频道",
        "激活平台 Wangpai",
    ]
    
    for msg in messages:
        msg_id = annotator.add_message(msg)
        print(f"Ajouté: {msg_id}")
    
    # Annoter le premier message
    unannotated = annotator.get_unannotated_messages()
    if unannotated:
        first = unannotated[0]
        annotator.annotate_message(
            first["id"],
            action="activate",
            target_type="platform",
            identifier="Wangpai",
            confidence=0.95
        )
        print(f"✅ Annoté: {first['id']}")
    
    # Afficher les stats
    stats = annotator.get_stats()
    print(f"\n📊 Stats:")
    print(f"  Total: {stats['total_messages']}")
    print(f"  Annotés: {stats['annotated']}")
    print(f"  Progrès: {stats['progress_percent']}%")
    
    # Exporter les données d'entraînement
    annotator.export_training_data()
