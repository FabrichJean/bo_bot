# Configuration du système d'annotation et test

# Ports des applications
ANNOTATION_APP_PORT = 5000
MODEL_TESTER_PORT = 5001
DEBUG_MODE = True

# Fichiers de données
DATA_FILES = {
    "training_data": "training_data.json",
    "annotated_messages": "annotated_messages.json",
    "test_feedback": "test_feedback.json",
    "sample_messages": "sample_messages_zh.json"
}

# Configuration RuleEngine
RULE_ENGINE_CONFIG = {
    "min_confidence": 0.3,
    "max_confidence": 1.0,
    "default_confidence": 0.5
}

# Configuration Feedback
FEEDBACK_CONFIG = {
    "confidence_increase_correct": 0.03,  # +3% pour "correct"
    "confidence_increase_corrected": 0.02,  # +2% pour "corrigé"
    "confidence_increase_wrong": 0.0,  # Pas d'amélioration pour "faux"
    "min_examples_per_rule": 1
}

# Mode d'Apprentissage Rapide (optionnel)
FAST_LEARNING_MODE = {
    "enabled": False,  # Mettre à True pour apprentissage rapide
    "confidence_increase_correct": 0.05,  # +5% au lieu de +3%
    "confidence_increase_corrected": 0.04,  # +4% au lieu de +2%
    "min_messages_before_fast_mode": 10  # Activer après 10 messages
}

# Configuration Annotation
ANNOTATION_CONFIG = {
    "simplified_only": True,  # Convertir en chinois simplifié
    "tokenization": "character",  # Tokenization par caractère
    "supported_languages": ["chinese", "english", "mixed"]
}

# Messages d'exemple pour test
EXAMPLE_MESSAGES_ZH = [
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
    },
    {
        "message": "停用 WeChat 平台",
        "expected_action": "deactivate",
        "expected_type": "platform",
        "expected_id": "WeChat"
    },
    {
        "message": "激活所有频道",
        "expected_action": "activate",
        "expected_type": "channel",
        "expected_id": "all"
    }
]

# Mots-clés par catégorie
ACTION_KEYWORDS = {
    "activate": ["启用", "打开", "开启", "激活"],
    "deactivate": ["关闭", "禁用", "停用", "关停"]
}

TARGET_KEYWORDS = {
    "platform": ["平台", "Platform"],
    "channel": ["频道", "Channel"]
}

# Thresholds pour l'interface
CONFIDENCE_THRESHOLDS = {
    "high": 0.80,    # Vert
    "medium": 0.60,  # Orange
    "low": 0.0       # Rouge
}

# Statistiques
STATS_CONFIG = {
    "accuracy_threshold_excellent": 0.90,
    "accuracy_threshold_good": 0.75,
    "accuracy_threshold_acceptable": 0.60,
    "accuracy_threshold_poor": 0.0
}

# Limites de pagination
PAGINATION = {
    "history_page_size": 50,
    "results_page_size": 20
}

# Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "system.log"
}
