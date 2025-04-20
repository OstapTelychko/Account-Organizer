from __future__ import annotations
from typing import TYPE_CHECKING
import os
import shutil
import concurrent.futures

from sys import platform
from zipfile import ZipFile
from pathlib import Path
from sqlalchemy import create_engine

import requests as req
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from alembic import command
from alembic.config import Config

from PySide6.QtCore import QTimer

from project_configuration import LATEST_RELEASE_URL, UPDATE_DIRECTORY, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP,\
GUI_LIBRARY, PREVIOUS_VERSION_COPY_DIRECTORY, ROOT_DIRECTORY, DEVELOPMENT_MODE,\
MOVE_FILES_TO_UPDATE, VERSION_FILE_NAME, ALEMBIC_CONFIG_FILE, BACKUPS_DIRECTORY_NAME

from languages import LanguageStructure

from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger

try:
    from tokens_ssh_gdp_secrets import UPDATE_API_TOKEN#This file is not included in repository. Token have to be provided by user to exceed rate limit of github api
except ImportError:
    UPDATE_API_TOKEN = None

if TYPE_CHECKING:
    from AppObjects.backup import Backup


logger = get_logger(__name__)


def requests_retry_session(retries:int = 3, backoff_factor:int = 0.3, status_forcelist:tuple = (429, 500, 502, 503, 504)):
    """Create a requests session with retry logic.

        Arguments
        ---------
        `retries`: (int) - The number of retries to attempt.

        `backoff_factor`: (int) - The backoff factor to apply between attempts (delay).

        `status_forcelist`: (tuple) - A set of HTTP status codes that we should force a retry on.
    """

    request_session = req.Session()
    retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    request_session.mount("https://", adapter)
    request_session.mount("http://", adapter)
    return request_session


def check_internet_connection() -> bool:
    """Check if internet connection is available by sending a HEAD request to google.com.

        Returns
        -------
        `bool`: True if internet connection is available, False otherwise.
    """

    try:
        response = req.head("https://www.google.com/", timeout=5)
        response.raise_for_status()
        return True
    except (req.exceptions.Timeout, req.exceptions.ConnectionError):
        logger.error("Check your internet connection.")
        return False
    
    except req.exceptions.TooManyRedirects:
        logger.error("Too many redirects.")
        return False
    
    except req.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        return False


def get_latest_version() -> str:
    """Get the latest version of the app from GitHub releases.
        Returns
        -------
        `str`: The latest version of the app.
    """

    logger.info("Checking for internet connection")
    if not check_internet_connection():
        return
    
    try:
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(LATEST_RELEASE_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(LATEST_RELEASE_URL, timeout=15)
        response.raise_for_status()

        latest_version = response.json()["tag_name"]
        return latest_version
    
    except req.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")


def download_latest_update() -> bool:
    """Download the latest update from GitHub releases.

        Returns
        -------
        `bool`: True if the download was successful, False otherwise.
    """

    try:
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(LATEST_RELEASE_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(LATEST_RELEASE_URL, timeout=15)
        response.raise_for_status()
        assets = response.json()["assets"]

        for asset in assets:
            if platform == "win32":
                if asset["name"] == WINDOWS_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    total_size = int(asset["size"])
                    logger.info(f"Starting download of {WINDOWS_UPDATE_ZIP}")
                    logger.debug(f"Download url: {download_url} | Size: {total_size}")
                    break
            else:
                if asset["name"] == LINUX_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    total_size = int(asset["size"])
                    logger.info(f"Starting download of {LINUX_UPDATE_ZIP}")
                    logger.debug(f"Download url: {download_url} | Size: {total_size}")
                    break

        WindowsRegistry.UpdateProgressWindow.download_label.setText(LanguageStructure.Update.get_translation(2).replace("update_size", str(round(total_size/1024/1024, 2))))
        
        download_response = req.get(download_url, stream=True, timeout=15)
        download_response.raise_for_status()

        chunk_size = 1024 * 256 #256KB
        download_size = 0

        if os.path.exists(UPDATE_DIRECTORY):
            logger.debug("Deleting previous update directory")
            shutil.rmtree(UPDATE_DIRECTORY)
        os.makedirs(UPDATE_DIRECTORY)
        logger.debug("Created update directory")

        logger.info("Saving update on disk")
        with open(f"{UPDATE_DIRECTORY}/{asset['name']}", "wb") as file:
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                download_size += len(chunk)
                file.write(chunk)
                WindowsRegistry.UpdateProgressWindow.download_progress.setValue((download_size/total_size)*100)
        logger.info("Update saved on disk")

        with ZipFile(f"{UPDATE_DIRECTORY}/{asset['name']}", "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIRECTORY)
        logger.info("Update extracted")
        return True

    except req.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return False
    
    except (req.exceptions.ConnectionError, req.exceptions.Timeout):
        logger.error("Internet connection was lost during download.")
        WindowsRegistry.Messages.no_internet.exec()
        WindowsRegistry.UpdateProgressWindow.done(1)
        return False
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        return False


def prepare_update():
    """Prepare the update by copying the GUI library and creating backups of the database files."""

    logger.info("Preparing update")

    if os.path.exists(PREVIOUS_VERSION_COPY_DIRECTORY):
        shutil.rmtree(PREVIOUS_VERSION_COPY_DIRECTORY)
        logger.info("Deleted previous version copy directory")
    
    logger.debug("Creating previous version copy directory")
    if DEVELOPMENT_MODE:#if app in development
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME))
    else:
        shutil.copytree(os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME))
    logger.debug("Created previous version copy directory")

    if DEVELOPMENT_MODE:
        GUI_LIBRARY_CURRENT_PATH = os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal", GUI_LIBRARY)
    else:
        GUI_LIBRARY_CURRENT_PATH = os.path.join(ROOT_DIRECTORY, "_internal", GUI_LIBRARY)

    GUI_LIBRARY_UPDATE_PATH = os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)
    if not os.path.exists(GUI_LIBRARY_UPDATE_PATH):#GUI library is removed from update to reduce size of update. If it already exists it means GUI library was updated
        shutil.copytree(GUI_LIBRARY_CURRENT_PATH, GUI_LIBRARY_UPDATE_PATH)
        logger.info("Copied GUI library to update directory")
    
    for file in MOVE_FILES_TO_UPDATE:
        shutil.copy2(file, os.path.join(UPDATE_DIRECTORY, "_internal"))
        logger.debug(f"Copied {file} to update directory")
    
    UPDATE_BACKUPS_DIRECTORY = os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME)
    os.makedirs(UPDATE_BACKUPS_DIRECTORY)
    logger.debug("Created update backups directory")

    if platform == "linux":
        os.chmod(os.path.join(UPDATE_DIRECTORY, "main"), 0o755)#The octal value 0o755 sets these file permissions: • Owner: Read/write/execute • Group: Read/execute • Others: Read/execute
        logger.debug("Changed main file permissions")

    with open(os.path.join(UPDATE_DIRECTORY, "_internal", VERSION_FILE_NAME)) as file:
        update_version = file.read()

    WindowsRegistry.UpdateProgressWindow.backups_upgrade_progress.setRange(0, len(Session.backups))
    upgraded_backups = 0

    logger.info("Creating and migrating backups")
    def _create_single_backup(backup:Backup):
        """Create a copy of the backup and upgrade it version but doesn't upgrade the database schema."""

        updated_backup_file_path = os.path.join(UPDATE_BACKUPS_DIRECTORY, f"Accounts_{backup.timestamp}_{update_version}.sqlite")
        Session.db.backup_query.create_backup_based_on_external_db(backup.db_file_path, updated_backup_file_path)
        logger.debug(f"Created backup: {updated_backup_file_path}")
        return updated_backup_file_path
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_create_single_backup, backup): backup for backup in Session.backups.values()}
        updated_backups_paths = [future.result() for future in futures]

    def _migrate_single_backup(backup_path:str):
        """Upgrade the copied backup database schema to the latest version."""

        nonlocal upgraded_backups

        alembic_config = Config(os.path.join(UPDATE_DIRECTORY, "_internal", ALEMBIC_CONFIG_FILE))
        alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{backup_path}")
        alembic_config.set_main_option("script_location", os.path.join(UPDATE_DIRECTORY, "_internal", "alembic"))

        engine = create_engine(f"sqlite:///{backup_path}")
        try:
            if not Session.db.db_up_to_date(alembic_config, engine):
                command.upgrade(alembic_config, "head")
        finally:
            engine.dispose()
        
        logger.debug(f"Migrated backup: {backup_path}")
        upgraded_backups += 1
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_migrate_single_backup, backup_path): backup_path for backup_path in updated_backups_paths}
        for future in futures:
            future.result()
            WindowsRegistry.UpdateProgressWindow.backups_upgrade_progress.setValue(upgraded_backups)
    logger.info("Backups created and migrated")
    
    logger.info("Move legacy backups to update directory")
    for backup in Session.backups.values():
        if not os.path.exists(os.path.join(UPDATE_BACKUPS_DIRECTORY, Path(backup.db_file_path).name)):
            if DEVELOPMENT_MODE:# I don't want to delete backups in development
                shutil.copy2(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
            else:
                shutil.move(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
            logger.debug(f"Moved backup: {backup.db_file_path}")
    
    logger.info("Update preparation finished")
        
        
def apply_update():
    """Apply the update by moving files and."""

    logger.info("Applying update")
    Session.db.close_connection()

    if DEVELOPMENT_MODE:#if app in development
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), os.path.join(ROOT_DIRECTORY, "dist", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME))
        logger.debug("Move update backups directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), os.path.join(ROOT_DIRECTORY, "dist", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        if platform == "win32":
            shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main.exe"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"))
        else:
            shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "main"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(3)

    else:
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(os.path.join(ROOT_DIRECTORY, "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME))
        logger.debug("Move update backups directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        if platform == "win32":
            shutil.move(os.path.join(ROOT_DIRECTORY, "main.exe"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main.exe"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "main.exe"))
        else:
            shutil.move(os.path.join(ROOT_DIRECTORY, "main"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(3)
    
    logger.debug("Deleting update directory")
    shutil.rmtree(UPDATE_DIRECTORY)

    WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(4)
    WindowsRegistry.UpdateProgressWindow.done(0)
    WindowsRegistry.MainWindow.raise_()
    WindowsRegistry.MainWindow.activateWindow()
    logger.info("Update applied")

    WindowsRegistry.Messages.update_finished.exec()
    Session.restart_app()


def check_for_updates():
    """Check for updates and ask to download them if available."""

    logger.info("__BREAK_LINE__")
    logger.info("Checking for updates")
    latest_version = get_latest_version()

    if latest_version:
        if latest_version == Session.app_version:
            logger.info("No updates available")
            logger.info("__BREAK_LINE__")
            return
        
        logger.info(f"Latest version: {latest_version} | Current version: {Session.app_version}")
        WindowsRegistry.Messages.update_available.exec()
        if WindowsRegistry.Messages.update_available.clickedButton() == WindowsRegistry.Messages.update_available.ok_button:
            
            def _run_update():
                logger.info("Running update")
                if download_latest_update():
                    logger.info("Downloaded latest update")
                    prepare_update()
                    apply_update()

            QTimer.singleShot(150, _run_update)
            WindowsRegistry.UpdateProgressWindow.exec()
    else:
        return WindowsRegistry.Messages.failed_update_check.exec()