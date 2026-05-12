
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
# Fonction asynchrone pour usage dans un handler async
async def async_screenshot_with_token(url: str, token: str, token_key: str = 'admin_token', screenshot_path: str = 'screenshot.png', element_selector = None) -> bytes:
    """
    Version asynchrone pour contexte asyncio (ex: handler Telethon).
    Affiche un message explicite si les navigateurs Playwright ne sont pas installés.
    :param url: URL à visiter
    :param token: Valeur du token à insérer dans le localStorage
    :param token_key: Clé du token dans le localStorage (par défaut 'admin_token')
    :param screenshot_path: Chemin où sauvegarder la capture (par défaut 'screenshot.png')
    :param element_selector: Sélecteur CSS pour capturer un élément spécifique (optionnel)
    :return: Image PNG en bytes
    """
    try:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
            except Exception as e:
                msg = str(e)
                if 'Executable doesn\'t exist' in msg or 'Please run the following command to download new browsers' in msg:
                    print("\n[ERREUR Playwright] Les navigateurs ne sont pas installés.\n" \
                          "Exécutez la commande suivante dans votre terminal :\n\n    playwright install\n")
                raise
            page = await browser.new_page()
            await page.goto(url)
            # Injecte le token dans le localStorage
            await page.evaluate(f"window.localStorage.setItem('{token_key}', '{token}')")
            await page.reload()
            await page.wait_for_load_state('networkidle')
            
            # Si un sélecteur est fourni, capture l'élément spécifique
            if element_selector:
                await page.wait_for_selector(element_selector, timeout=10000)
                element = await page.query_selector(element_selector)
                if element:
                    img_bytes = await element.screenshot(path=screenshot_path)
                else:
                    print(f"[ERREUR] Élément non trouvé avec le sélecteur : {element_selector}")
                    img_bytes = await page.screenshot(path=screenshot_path)
            else:
                # Capture la page entière
                img_bytes = await page.screenshot(path=screenshot_path)
            
            await browser.close()
            return img_bytes
    except Exception as e:
        # Pour remonter l'erreur au handler appelant
        raise


def screenshot_with_token(url: str, token: str, token_key: str = 'token', screenshot_path: str = 'screenshot.png') -> bytes:
    """
    Ouvre un navigateur, insère le token dans le localStorage, recharge la page, prend une capture d'écran et retourne l'image (bytes).
    :param url: URL à visiter
    :param token: Valeur du token à insérer dans le localStorage
    :param token_key: Clé du token dans le localStorage (par défaut 'token')
    :param screenshot_path: Chemin où sauvegarder la capture (par défaut 'screenshot.png')
    :return: Image PNG en bytes
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # Injecte le token dans le localStorage
        page.evaluate(f"window.localStorage.setItem('{token_key}', '{token}')")
        # Recharge la page pour être authentifié
        page.reload()
        # Attendre que la page soit chargée (optionnel: adapte le sélecteur)
        page.wait_for_load_state('networkidle')
        # Capture d'écran
        img_bytes = page.screenshot(path=screenshot_path)
        browser.close()
        return img_bytes

# Exemple d'utilisation
if __name__ == '__main__':
    url = 'https://example.com/dashboard'  # Remplace par l'URL cible
    token = 'votre_token_ici'
    image_bytes = screenshot_with_token(url, token)
    print(f'Capture sauvegardée dans screenshot.png, taille: {len(image_bytes)} octets')
