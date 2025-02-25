import os
import shutil
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.entities.file_type import FileType
from app.logs.config_scraper_logs import scraper_logger
from app.logs.config_server_logs import server_logger


def click_download_button(driver, file_type: FileType):
    """Clique sur le bouton 'EXCEL' pour télécharger le fichier."""
    wait = WebDriverWait(driver, 15)

    scraper_logger.info(f"🔎 Recherche du bouton '{file_type.value}'...")

    if file_type == FileType.XLSX:
        element = "/html/body/div[1]/div[3]/div[3]/div/div[1]/a[3]"
    elif file_type == FileType.CSV:
        element = "/html/body/div[1]/div[3]/div[3]/div/div[1]/a[2]"
    else:
        server_logger.error(f" File type not supported.")
        raise NotImplementedError

    download_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, element))
    )
    time.sleep(5)

    scraper_logger.info(f"🖱 Clic sur le bouton '{file_type}'...")
    driver.execute_script("arguments[0].click();", download_button)
    scraper_logger.info(f"✅ Clic sur '{file_type}' effectué.")

    time.sleep(5)


def move_and_rename_file(download_path: str, dest_path: str, file_type: FileType) -> str | None:
    """Attente, vérification, renommage et déplacement du fichier téléchargé."""
    downloads_path = download_path

    project_root = Path(__file__).resolve().parent.parent.parent.parent

    destination_path = project_root / dest_path

    # 🔹 Attendre que le fichier soit téléchargé
    scraper_logger.info("⏳ Attente du fichier téléchargé...")
    timeout = 30  # Temps maximum d'attente (secondes)
    elapsed_time = 0
    downloaded_file = None

    while elapsed_time < timeout:
        # Liste des fichiers .xlsx triés par date de création
        if file_type == FileType.XLSX:
            download_files = [f for f in os.listdir(downloads_path) if f.endswith(".xlsx")]
        elif file_type == FileType.CSV:
            download_files = [f for f in os.listdir(downloads_path) if f.endswith(".csv")]
        else:
            server_logger.error(f" File type not supported.")
            raise NotImplementedError

        if download_files:
            downloaded_file = max(download_files, key=lambda f: os.path.getctime(os.path.join(downloads_path, f)))
            scraper_logger.info(f"✅ Fichier détecté : {downloaded_file}")
            break  # Sortir de la boucle dès qu'un fichier est détecté

        time.sleep(1)
        elapsed_time += 1

    if not downloaded_file:
        scraper_logger.info("❌ ERREUR : Aucun fichier téléchargé après l'attente.")

    downloaded_file_path = os.path.join(downloads_path, downloaded_file)

    # 🔹 Générer un nouveau nom avec la date et l'heure
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = f"CapuDiMuru_{timestamp}{file_type.value}"
    new_path = os.path.join(destination_path, new_filename)

    # 🔹 Renommer et déplacer le fichier
    try:
        shutil.move(downloaded_file_path, new_path)
        scraper_logger.info(f"✅ Fichier renommé et déplacé vers : {new_path}")
        return new_path
    except Exception as e:
        scraper_logger.error(f"❌ ERREUR lors du déplacement du fichier : {e}")
        return None
