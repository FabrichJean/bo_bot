# Configuration centralisée pour le bot Telegram

# --- TELEGRAM API ---
TELEGRAM_API_ID = 37308629
TELEGRAM_API_HASH = '698a893741a1019d222c87b9a53851c3'
TELEGRAM_SESSION_NAME = 'session_bobot'

# --- GROUPES ---
GROUP_MAIN = '91bot运维通知群'
GROUP_ID_TEST = -5142068832


# --- CONNEXION ---
CONNECTION_RETRIES = -1  # Tentatives infinies
RETRY_DELAY = 5  # Secondes entre chaque tentative
AUTO_RECONNECT = True

# --- JWT & API ---
JWT_SECRET = '49caa9850a1abdf6fghrdf5a9fb093c44aac84dbc46b1f7ab7e4d5c252306919cbdf81'
BASE_URL = 'https://xo-back.99sq20.fun'

# --- Payload Admin par défaut ---
ADMIN_PAYLOAD = {
    "id": "296952048098738236",
    "username": "admin",
    "role": "admin",
    "code": "123456",
    "parent_id": "123456"
}

# --- FICHIERS ---
REGISTRATION_CODES_FILE = 'registration_codes.txt'
AUTHORIZED_USERS_FILE = 'authorized_users.json'

# --- SCREENSHOTS ---
SCREENSHOT_ADMIN_URL = 'https://xo-admin.99sq20.fun/admin/exchange/payment-platforms?search=Wangpai&toggleFirst=true'
SCREENSHOT_ROOT_DIR = 'screenshots'  # Dossier racine pour tous les screenshots
SCREENSHOT_ELEMENT_SELECTOR = 'div.va-card__content'

# --- RAPPORT/TEST LISTENER ---
RAPPORT_TEST_SAVE_DESTINATION = '5205859116'  # ID, username ou 'me' pour les Saved Messages

# --- COMMANDES ---
COMMAND_PREFIX = '/'

# --- TRADUCTION ---
TRANSLATE_TARGET_LANG = 'fr'
TRANSLATE_SOURCE_LANG = 'auto'

# --- MESSAGE LEARNING SYSTEM ---
MESSAGE_RULES_FILE = 'message_rules.json'
LEARNING_HISTORY_FILE = 'learning_history.json'

# Seuils de confiance pour l'exécution automatique
CONFIDENCE_THRESHOLDS = {
    'auto_execute': 0.90,        # ≥0.90 → exécuter directement
    'ask_confirmation': 0.70,    # 0.70-0.89 → demander confirmation
    'reject': 0.0                # <0.70 → rejeter
}

# Apprentissage
LEARNING_CONFIG = {
    'enable_learning': True,      # Activer l'apprentissage
    'validate_feedback': True,    # Demander /validate après action
    'learn_from_success': True,   # Augmenter confiance si succès
    'confidence_increment': 0.02, # +2% par validation
    'confidence_decrement': 0.05, # -5% si rejet
    'keep_history': True,         # Garder tout l'historique
    'max_examples_per_rule': 10   # Max d'exemples stockés
}

# Actions supportées
SUPPORTED_ACTIONS = {
    'activate': ['activate', 'enable', 'turn on', 'on', 'active'],
    'deactivate': ['deactivate', 'disable', 'turn off', 'off', 'inactive']
}

# Types de cibles supportées
SUPPORTED_TARGET_TYPES = {
    'platform': ['platform', 'plateforme', 'système'],
    'channel': ['channel', 'canal', 'voie']
}
