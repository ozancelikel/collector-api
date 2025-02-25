import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.config import settings
from app.logs.config_scraper_logs import scraper_logger


def init_driver(visibility: bool = True):
    """Initialise Selenium et retourne le WebDriver."""
    options = webdriver.ChromeOptions()
    if visibility is False:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")  # Force desktop resolution
        options.add_argument("--force-device-scale-factor=1")  # Avoid zooming issues
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        # options.add_argument("--window-size=1920x1080")
        scraper_logger.info("⚠️ Option Headless !")

    # Si platform est Linux, specifiez le path de Chromium browser
    if sys.platform != "win32":
        options.binary_location = "/usr/bin/chromium-browser"

    # Set viewport
    driver = webdriver.Chrome(options=options)
    scraper_logger.info(" Driver window size: ", driver.get_window_rect())  # Should show {'width': 1920, 'height': 1080}
    return driver


def login_to_konect(driver: webdriver, username: str, password: str):
    """Connexion à KonectGDS avec Selenium."""
    try:
        scraper_logger.info("🌐 Connexion à KonectGDS...")
        driver.get(settings.KONECTGDS_URL)
        time.sleep(3)

        # **Attendre que les champs d’identifiants soient prêts**
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PassportID"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Password"))
        )

        scraper_logger.info("✅ Champs trouvés.")

        # **Effacer les champs avant d’écrire**
        username_field.clear()
        password_field.clear()
        time.sleep(1)

        # **Saisie des identifiants (simulation humaine)**
        for char in username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        scraper_logger.info("✅ Identifiant saisi.")

        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        scraper_logger.info("✅ Mot de passe saisi.")

        # **Validation par ENTER**
        password_field.send_keys(Keys.RETURN)
        scraper_logger.info("✅ ENTER pressé pour valider la connexion.")

        # **Attendre la connexion**
        time.sleep(5)

        # **Vérifier si la connexion a réussi**
        if "login" in driver.current_url.lower():
            scraper_logger.info("❌ Échec de l'authentification.")
            driver.quit()
            sys.exit("⛔ Arrêt du script.")

        scraper_logger.info("✅ Connexion réussie.")
        return driver  # Retourne le WebDriver après connexion

    except Exception as e:
        driver.quit()
        scraper_logger.error(f"❌ Erreur lors de la connexion : {e}")
