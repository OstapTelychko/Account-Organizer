import os
import shutil
import concurrent.futures

from sys import platform
from zipfile import ZipFile
from sqlalchemy import create_engine

import requests as req
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from alembic import command
from alembic.config import Config

from PySide6.QtCore import QTimer, QObject, QThread, Signal

from project_configuration import LATEST_RELEASE_URL, UPDATE_DIRECTORY, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP,\
GUI_LIBRARY, PREVIOUS_VERSION_COPY_DIRECTORY, ROOT_DIRECTORY, APP_DIRECTORY,\
MOVE_FILES_TO_UPDATE, VERSION_FILE_NAME, ALEMBIC_CONFIG_FILE, BACKUPS_DIRECTORY_NAME
from languages import LANGUAGES

from GUI.windows.messages import Messages
from GUI.windows.update_progress import UpdateProgressWindow

from AppObjects.session import Session
from AppObjects.backup import Backup

try:
    from tokens_ssh_gdp_secrets import UPDATE_API_TOKEN#This file is not included in repository. Token have to be provided by user to exceed rate limit of github api
except ImportError:
    UPDATE_API_TOKEN = None



class CheckForUpdatesWorker(QObject):
    finished = Signal()
    error = Signal(Exception)

    def run(self, check_function):
        try:
            check_function()
        except Exception as e:
            self.error.emit(e)
        self.finished.emit()



def requests_retry_session(retries:int = 3, backoff_factor:int = 0.3, status_forcelist:tuple = (429, 500, 502, 503, 504)):
    request_session = req.Session()
    retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    request_session.mount("https://", adapter)
    request_session.mount("http://", adapter)
    return request_session


def check_internet_connection() -> bool:
    try:
        response = req.head("https://www.google.com/", timeout=5)
        response.raise_for_status()
        return True
    except (req.exceptions.Timeout, req.exceptions.ConnectionError):
        print("Check your internet connection.")
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
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(LATEST_RELEASE_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(LATEST_RELEASE_URL, timeout=15)
        response.raise_for_status()

        latest_version = response.json()["tag_name"]
        return latest_version
    
    except req.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")


def download_latest_update() -> bool:
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
                    break
            else:
                if asset["name"] == LINUX_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    total_size = int(asset["size"])
                    break

        UpdateProgressWindow.download_label.setText(LANGUAGES[Session.language]["Windows"]["Update"][2].replace("update_size", str(round(total_size/1024/1024, 2))))
        
        download_response = req.get(download_url, stream=True, timeout=15)
        download_response.raise_for_status()

        chunk_size = 1024 * 256 #256KB
        download_size = 0

        if os.path.exists(UPDATE_DIRECTORY):
            shutil.rmtree(UPDATE_DIRECTORY)
        os.makedirs(UPDATE_DIRECTORY)

        with open(f"{UPDATE_DIRECTORY}/{asset['name']}", "wb") as file:
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                download_size += len(chunk)
                file.write(chunk)
                UpdateProgressWindow.download_progress.setValue((download_size/total_size)*100)

        with ZipFile(f"{UPDATE_DIRECTORY}/{asset['name']}", "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIRECTORY)
        return True

    except req.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return False
    
    except (req.exceptions.ConnectionError, req.exceptions.Timeout):
        Messages.no_internet.exec()
        UpdateProgressWindow.window.done(1)
        return False
    
    except Exception as e:
        print(f"Unexpected exception: {e}")
        return False


def prepare_update():

    if os.path.exists(PREVIOUS_VERSION_COPY_DIRECTORY):
        shutil.rmtree(PREVIOUS_VERSION_COPY_DIRECTORY)
    
    if ROOT_DIRECTORY == APP_DIRECTORY:#if app in development
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME))
        if platform == "win32":
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"), PREVIOUS_VERSION_COPY_DIRECTORY)
        else:
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main"), PREVIOUS_VERSION_COPY_DIRECTORY)

    else:
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
        shutil.copytree(os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME))
        if platform == "win32":
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "main.exe"), PREVIOUS_VERSION_COPY_DIRECTORY)
        else:
            shutil.copy2(os.path.join(ROOT_DIRECTORY, "main"), PREVIOUS_VERSION_COPY_DIRECTORY)
    
    GUI_LIBRARY_PATH_CURRENT = os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal", GUI_LIBRARY)
    GUI_LIBRARY_PATH_UPDATE = os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)
    if not os.path.exists(GUI_LIBRARY_PATH_UPDATE):#GUI library is removed from update to reduce size of update. If it already exists it means GUI library was updated
        shutil.copytree(GUI_LIBRARY_PATH_CURRENT, GUI_LIBRARY_PATH_UPDATE)
    
    for file in MOVE_FILES_TO_UPDATE:
        shutil.copy2(file, os.path.join(UPDATE_DIRECTORY, "_internal"))
    
    UPDATE_BACKUPS_DIRECTORY = os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME)
    os.makedirs(UPDATE_BACKUPS_DIRECTORY)

    if platform == "linux":
        os.chmod(os.path.join(UPDATE_DIRECTORY, "main"), 0o755)#The octal value 0o755 sets these file permissions: • Owner: Read/write/execute • Group: Read/execute • Others: Read/execute

    with open(os.path.join(UPDATE_DIRECTORY, "_internal", VERSION_FILE_NAME)) as file:
        update_version = file.read()

    UpdateProgressWindow.backups_upgrade_progress.setRange(0, len(Session.backups))
    upgraded_backups = 0

    def _create_single_backup(backup:Backup):
        updated_backup_file_path = os.path.join(UPDATE_BACKUPS_DIRECTORY, f"Accounts_{backup.timestamp}_{update_version}.sqlite")
        Session.db.create_backup_based_on_external_db(backup.db_file_path, updated_backup_file_path)
        return updated_backup_file_path
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_create_single_backup, backup): backup for backup in Session.backups.values()}
        updated_backups_paths = [future.result() for future in futures]

    def _migrate_single_backup(backup_path:str):
        nonlocal upgraded_backups

        alembic_config = Config(os.path.join(UPDATE_DIRECTORY, "_internal", ALEMBIC_CONFIG_FILE))
        alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{backup_path}")
        alembic_config.set_main_option("script_location", os.path.join(UPDATE_DIRECTORY, "_internal", "alembic"))

        engine = create_engine(f"sqlite:///{backup_path}")
        if not Session.db.db_up_to_date(alembic_config, engine):
            command.upgrade(alembic_config, "head")
        
        upgraded_backups += 1
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(_migrate_single_backup, backup_path): backup_path for backup_path in updated_backups_paths}
        for future in futures:
            future.result()
            UpdateProgressWindow.backups_upgrade_progress.setValue(upgraded_backups)
    
    for backup in Session.backups.values():
        if APP_DIRECTORY == ROOT_DIRECTORY:# I don't want to delete backups in development
            shutil.copy2(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
        else:
            shutil.move(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
        
        
def apply_update():
    UpdateProgressWindow.apply_update_progress.show()
    if ROOT_DIRECTORY == APP_DIRECTORY:#if app in development
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"))
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), os.path.join(ROOT_DIRECTORY, "dist", "main"))

        shutil.rmtree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME))
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), os.path.join(ROOT_DIRECTORY, "dist", "main"))

        if platform == "win32":
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"))
        else:
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main"))

    else:
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, "_internal"))
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), ROOT_DIRECTORY)

        shutil.rmtree(os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME))
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), ROOT_DIRECTORY)

        if platform == "win32":
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "main.exe"))
        else:
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "main"))
    
    shutil.rmtree(UPDATE_DIRECTORY)





def check_for_updates():

    def _check():
        latest_version = get_latest_version()

        if latest_version:
            if latest_version == Session.app_version:
                return
            
            Messages.update_available.exec()
            if Messages.update_available.clickedButton() == Messages.update_available.ok_button:
                def _run_update():
                    if download_latest_update():
                        prepare_update()
                        apply_update()
                    UpdateProgressWindow.apply_update_progress.hide()
                    UpdateProgressWindow.window.done(0)
                QTimer.singleShot(150, _run_update)
                UpdateProgressWindow.window.exec()
        else:
            return Messages.failed_update_check.exec()
    
    worker = CheckForUpdatesWorker()
    thread = QThread()
    thread_id = id(thread)
    Session.qthreads[thread_id] = thread
    worker.moveToThread(thread)
    thread.started.connect(lambda: worker.run(_check))

    # worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(lambda thread_id=thread_id: Session.qthreads.pop(thread_id))
    thread.start()
