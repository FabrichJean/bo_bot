import requests

from config import TRANSLATE_SOURCE_LANG, TRANSLATE_TARGET_LANG


def google_translate(text, target_lang=TRANSLATE_TARGET_LANG):
    """Traduit un texte via l'API Google Translate."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={TRANSLATE_SOURCE_LANG}&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        # L'API renvoie une liste de listes, la traduction est dans le premier élément
        return response.json()[0][0][0]
    except Exception as e:
        return f"[Erreur traduction: {e}]"
