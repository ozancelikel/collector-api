import time
from datetime import datetime
import sys

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.logs.config_scraper_logs import scraper_logger


def open_task_query(driver, hourly: bool=True):
    """Navigue jusqu'à la section Table Query après connexion."""
    wait = WebDriverWait(driver, 20)

    # Ouvrir la section "Tasks"
    scraper_logger.info("🖱 Clic sur le bouton 'Tasks'...")
    try:
        tasks_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[5]/div[2]/div[1]")))
        tasks_button.click()
    except TimeoutException:
        scraper_logger.info("⚠ Element not found within the timeout period!")
        driver.save_screenshot("debug_screenshot.png")
    time.sleep(2)

    # Ouvrir "Table Query"
    scraper_logger.info("🖱 Clic sur 'Table Query'...")
    table_query_menu = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[5]/div[2]/div/div/div[1]/div[5]/div[2]"))
    )
    table_query_menu.click()
    time.sleep(2)

    scraper_logger.info("✅ Onglet 'Table Query' ouvert.")

    # 🔹 Sélectionner la requête "CapuDiMuru_Data" si requete pour tous data
    # 🔹 Sinon, selectionner CapuDiMuru_Data_horaire
    if not hourly:
        scraper_logger.info("🔍 Sélection de la requête 'CapuDiMuru_Data'...")
        click_xpath = "/html/body/div[3]/div[9]/div[2]/div[2]/div/div/div[1]/div/div[2]"
    else:
        scraper_logger.info("🔍 Sélection de la requête 'CapuDiMuru_Data_horaire'...")
        click_xpath = "/html/body/div[3]/div[9]/div[2]/div[2]/div/div/div[1]/div[2]/div[2]"
    full_data_query = wait.until(
        EC.element_to_be_clickable((By.XPATH, click_xpath)))
    full_data_query.click()
    if not hourly:
        scraper_logger.info("✅ Requête 'CapuDiMuru_Data' sélectionnée.")
    else:
        scraper_logger.info("✅ Requête 'CapuDiMuru_Data_horaire' sélectionnée.")


def modify_query_date(driver, hourly: bool=True):
    """Modifie la date 'To' avec la date et heure actuelles après ouverture du menu déroulant."""
    wait = WebDriverWait(driver, 20)  # Augmentation du temps d'attente
    if not hourly:
        try:
            # 🔹 Vérifier la présence du bouton du menu
            scraper_logger.info("🖱 Vérification de la présence du menu déroulant...")
            menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/button")))

            # 🔹 Dérouler le menu
            driver.execute_script("arguments[0].scrollIntoView();", menu_button)
            time.sleep(1)  # Pause pour éviter les erreurs
            scraper_logger.info("📌 Clic sur le bouton du menu déroulant...")
            try:
                menu_button.click()
            except Exception as e:
                scraper_logger.error(f"⚠️ Clic direct échoué, tentative avec JavaScript... \nError Message: {e}")
                driver.execute_script("arguments[0].click();", menu_button)

            time.sleep(2)

            # 🔹 Vérifier si le menu s'est bien ouvert
            menu_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/ul")))
            scraper_logger.info("✅ Menu déroulant détecté.")

            # 🔹 Sélectionner "Change Data Range"
            scraper_logger.info("📌 Sélection de 'Change Data Range'...")
            change_data_range_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/ul/li[3]/a"))
            )
            driver.execute_script("arguments[0].click();", change_data_range_option)  # Forcer le clic si nécessaire
            time.sleep(2)

            # 🔹 Vérifier la présence du champ de date 'To'
            scraper_logger.info("🔍 Vérification du champ de date 'To'...")
            to_date_field = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='to']")))

            # 🔹 Générer la date et l'heure actuelles au format demandé
            now = datetime.now()
            if sys.platform == "win32":
                formatted_date = now.strftime("%#d %b %Y %H:%M")  # Windows
            else:
                formatted_date = now.strftime("%-d %b %Y %H:%M")  # Linux/Mac

            # 🔹 Effacer et modifier la date
            scraper_logger.info(f"📝 Modification de la date 'To' en : {formatted_date}")
            to_date_field.clear()
            to_date_field.send_keys(formatted_date)

            scraper_logger.info("✅ Date 'To' mise à jour avec succès.")

            time.sleep(2)


            # 🔹 Localiser et cliquer sur le bouton "Submit"
            scraper_logger.info("🖱 Clic sur le bouton 'Submit' pour valider la modification...")
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "// *[ @ id = 'submitbtn']")))  # Remplace avec le bon XPath si nécessaire

            driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            time.sleep(1)

            try:
                submit_button.click()
            except Exception as e:
                scraper_logger.error(f"⚠️ Clic direct sur 'Submit' échoué, tentative avec JavaScript... \nError Message: {e}")
                driver.execute_script("arguments[0].click();", submit_button)

            scraper_logger.info("✅ Modification validée avec succès !")

            time.sleep(2)
        except Exception as e:
            scraper_logger.info(f"❌ Erreur critique lors de la modification de la date : {e}")
            driver.save_screenshot("error_screenshot.png")  # Capture d'écran pour analyse
            driver.quit()  # Ferme le navigateur
            sys.exit(1)  # Stoppe l'exécution du programme
