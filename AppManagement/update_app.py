import requests as req
import os
import shutil
import concurrent.futures

from pathlib import Path
from sys import platform
from zipfile import ZipFile
from sqlalchemy import create_engine

from alembic import command
from alembic.config import Config

from project_configuration import LATEST_RELEASE_URL, UPDATE_DIRECTORY, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP,\
GUI_LIBRARY, CURRENT_VERSION_COPY_DIRECTORY, ROOT_DIRECTORY, APP_DIRECTORY,\
MOVE_FILES_TO_UPDATE, BACKUPS_DIRECTORY, VERSION_FILE_NAME, ALEMBIC_CONFIG_FILE

from AppObjects.session import Session
from AppObjects.backup import Backup



def check_internet_connection() -> bool:
    try:
        response = req.head("https://www.google.com/", timeout=5)
        response.raise_for_status()
        return True
    except req.exceptions.Timeout:
        print("Request timed out. Check your internet connection.")
        return False
    
    except req.exceptions.ConnectionError:
        print("Connection error. Check your internet connection.")
        return False
    
    except req.exceptions.TooManyRedirects:
        print("Too many redirects.")
        return False
    
    except req.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return False
    
    except Exception as e:
        print(f"Unexpected exception: {e}")
        return False


def get_latest_version():
    if not check_internet_connection():
        return 
    
    try:
        response = req.get(LATEST_RELEASE_URL)
        response.raise_for_status()
        latest_version = response.json()["tag_name"]
        return latest_version
    except req.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")


def download_latest_update():
    try:
        response = req.get(LATEST_RELEASE_URL)
        response.raise_for_status()
        assets = response.json()["assets"]

        for asset in assets:
            if platform == "win32":
                if asset["name"] == WINDOWS_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    break
            else:
                if asset["name"] == LINUX_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    break
        
        download_response = req.get(download_url, stream=True, timeout=15)
        download_response.raise_for_status()

        total_size = int(download_response.headers.get("content-length", 0))
        chunk_size = 1024 * 1024 #1MB
        download_size = 0

        if os.path.exists(UPDATE_DIRECTORY):
            shutil.rmtree(UPDATE_DIRECTORY)
        os.makedirs(UPDATE_DIRECTORY)

        with open(f"{UPDATE_DIRECTORY}/{asset['name']}", "wb") as file:
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                download_size += len(chunk)
                file.write(chunk)
                print(f"Downloaded {download_size/total_size:.2%}")
        print("Download complete.")

        with ZipFile(f"{UPDATE_DIRECTORY}/{asset['name']}", "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIRECTORY)
        print("Update extracted.")
        
    except req.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    
    except (req.exceptions.ConnectionError, req.exceptions.Timeout):
        print("Connection error. Check your internet connection.")
    
    except Exception as e:
        print(f"Unexpected exception: {e}")


def prepare_update():
    if os.path.exists(CURRENT_VERSION_COPY_DIRECTORY):
        shutil.rmtree(CURRENT_VERSION_COPY_DIRECTORY)
    
    if ROOT_DIRECTORY == APP_DIRECTORY:#if app in development
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"), os.path.join(CURRENT_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
        if platform == "win32":
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"), CURRENT_VERSION_COPY_DIRECTORY)
        else:
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main"), CURRENT_VERSION_COPY_DIRECTORY)

    else:
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "_internal"), os.path.join(CURRENT_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
        if platform == "win32":
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "main.exe"), CURRENT_VERSION_COPY_DIRECTORY)
        else:
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "main"), CURRENT_VERSION_COPY_DIRECTORY)
    
    GUI_LIBRARY_PATH_CURRENT = os.path.join(CURRENT_VERSION_COPY_DIRECTORY, "_internal", GUI_LIBRARY)
    GUI_LIBRARY_PATH_UPDATE = os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)
    if not os.path.exists(GUI_LIBRARY_PATH_UPDATE):#GUI library is removed from update to reduce size if it already exists it means GUI library was updated
        shutil.copytree(GUI_LIBRARY_PATH_CURRENT, GUI_LIBRARY_PATH_UPDATE)
    
    for file in MOVE_FILES_TO_UPDATE:
        shutil.copy2(file, os.path.join(UPDATE_DIRECTORY, "_internal"))
    
    UPDATE_BACKUPS_DIRECTORY = os.path.join(UPDATE_DIRECTORY, Path(BACKUPS_DIRECTORY).name)
    os.makedirs(UPDATE_BACKUPS_DIRECTORY)

    with open(os.path.join(UPDATE_DIRECTORY, "_internal", VERSION_FILE_NAME)) as file:
        update_version = file.read()

    def _create_single_backup(backup:Backup):
        updated_backup_file_path = os.path.join(UPDATE_BACKUPS_DIRECTORY, f"Accounts_{backup.timestamp}_{update_version}.sqlite")
        Session.db.create_backup_based_on_external_db(backup.db_file_path, updated_backup_file_path)
        return updated_backup_file_path
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_create_single_backup, backup): backup for backup in Session.backups.values()}
        updated_backups_paths = [future.result() for future in futures]

    def _migrate_single_backup(backup_path:str):
        alembic_config = Config(os.path.join(UPDATE_DIRECTORY, "_internal", ALEMBIC_CONFIG_FILE))
        alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{backup_path}")
        alembic_config.set_main_option("script_location", os.path.join(UPDATE_DIRECTORY, "_internal", "alembic"))

        engine = create_engine(f"sqlite:///{backup_path}")
        if not Session.db.db_up_to_date(alembic_config, engine):
            command.upgrade(alembic_config, "head")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_migrate_single_backup, backup_path): backup_path for backup_path in updated_backups_paths}
        for future in futures:
            future.result()
        
        
# def apply_update():




def check_for_updates():
    latest_version = get_latest_version()

    if latest_version:
        if latest_version != Session.app_version:
            download_latest_update()
            prepare_update()
            return f"Update available: {latest_version}"
        else:
            return "No updates available."
    else:
        return "Failed to check for updates."