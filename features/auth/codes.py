from config import REGISTRATION_CODES_FILE


def load_registration_codes():
    """Charge les codes d'enregistrement depuis le fichier."""
    try:
        with open(REGISTRATION_CODES_FILE, 'r') as f:
            codes = [line.strip().upper() for line in f if line.strip()]
        return codes
    except FileNotFoundError:
        return []


def remove_registration_code(code):
    """Supprime un code d'enregistrement du fichier après utilisation."""
    try:
        with open(REGISTRATION_CODES_FILE, 'r') as f:
            codes = [line.strip() for line in f if line.strip()]

        # Supprimer le code (insensible à la casse)
        codes = [c for c in codes if c.upper() != code.upper()]

        with open(REGISTRATION_CODES_FILE, 'w') as f:
            for code in codes:
                f.write(code + '\n')
    except Exception as e:
        print(f"Erreur lors de la suppression du code : {e}")
