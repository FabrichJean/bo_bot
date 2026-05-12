# Configuration centralisée pour le bot Telegram

# --- TELEGRAM API ---
TELEGRAM_API_ID = 37308629
TELEGRAM_API_HASH = '698a893741a1019d222c87b9a53851c3'
TELEGRAM_SESSION_NAME = 'session_bobot'

# --- GROUPES ---
GROUP_MAIN = '91bot运维通知群'
GROUP_ID_TEST = 5156646256

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

# --- COMMANDES ---
COMMAND_PREFIX = '/'

# --- TRADUCTION ---
TRANSLATE_TARGET_LANG = 'fr'
TRANSLATE_SOURCE_LANG = 'auto'
