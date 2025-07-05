from __future__ import annotations
from typing import TYPE_CHECKING
import json
import os
import hashlib
import shutil
from sys import platform
from zipfile import ZipFile, ZIP_DEFLATED

import requests as req
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry #type: ignore[import-not-found]

from languages import LanguageStructure
from project_configuration import LATEST_RELEASE_URL, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP, UPDATE_DIRECTORY, CHUNK_SIZE_FOR_FILE_HASHER, RELEASES_URL,\
WINDOWS_GUI_LIBRARY_ZIP, LINUX_GUI_LIBRARY_ZIP, CHUNK_SIZE_FOR_DOWNLOADING, ATTEMPTS_TO_DOWNLOAD_ZIP, GUI_LIBRARY_DIRECTORY, GUI_LIBRARY_DIRECTORY_ZIP,\
GUI_LIBRARY

from AppObjects.logger import get_logger
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry

try:
    from tokens_ssh_gdp_secrets import UPDATE_API_TOKEN#This file is not included in repository. Token have to be provided by user to exceed rate limit of github api
except ImportError:
    UPDATE_API_TOKEN:str|None = None#type: ignore[no-redef]

if TYPE_CHECKING:
    from typing import Any

    RELEASE = dict[str, Any]
    ASSETS = list[dict[str, Any]]
    UPDATE_ASSET = tuple[str, str, int, str]
    GUI_LIBRARY_ASSET = tuple[str, str, int, str]


logger = get_logger(__name__)


def generate_file_256hash(file_path: str) -> str:
    """Generate a SHA-256 hash of the file at the given path.

        Arguments
        ---------
        `file_path`: (str) - The path to the file to hash.

        Returns
        -------
        `str`: The SHA-256 hash of the file.

        Raises
        ------
        `FileNotFoundError`: If the file does not exist.

        Notes
        -----
        If you want to get hash for directory, you have to compress it into one file first.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}. Hash cannot be generated.")

    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}. Hash cannot be generated.")
    
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE_FOR_FILE_HASHER):
            hasher.update(chunk)

    return hasher.hexdigest()


def compress_directory(directory_path: str, output_zip_path: str) -> None:
    """Compress a directory into a zip file.

        Arguments
        ---------
        `directory_path`: (str) - The path to the directory to compress.

        `output_zip_path`: (str) - The path to the output zip file.
    """

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}. Cannot compress.")

    if not os.path.isdir(directory_path):
        raise ValueError(f"Path is not a directory: {directory_path}. Cannot compress.")

    with ZipFile(output_zip_path, "w", ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, rel_path)


def requests_retry_session(retries:int = 3, backoff_factor:float = 0.3, status_forcelist:tuple[int, ...] = (429, 500, 502, 503, 504)) -> req.Session:
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


def get_prerelease() -> RELEASE | None:
    """Get the latest prerelease version of the app from GitHub releases.

        Returns
        -------
        `RELEASE_TYPE | None`: The latest prerelease version of the app or None if not found.
    """
    
    try:
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(RELEASES_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(RELEASES_URL, timeout=15)
        response.raise_for_status()

        if response.status_code != 200:
            logger.error(f"Failed to get releases: {response.status_code}")
            return None

        releases:list[RELEASE] = response.json()
        for release in releases:
            if release.get("prerelease", False):
                return release
        
        return None
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        return None


def get_release() -> RELEASE | None:
    """Get the latest release version of the app from GitHub releases.

        Returns
        -------
        `RELEASE_TYPE | None`: The latest release version of the app or None if not found.
    """

    try:
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(LATEST_RELEASE_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(LATEST_RELEASE_URL, timeout=15)
        response.raise_for_status()

        if response.status_code != 200:
            logger.error(f"Failed to get latest release: {response.status_code}")
            raise RuntimeError(f"Failed to get latest release: {response.status_code}")

        release:RELEASE = response.json()
        return release
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        return None


def get_latest_version() -> tuple[str, RELEASE] | None:
    """Get the latest version of the app from GitHub releases.

        Returns
        -------
        `str`: The latest version of the app.
    """

    app_core = AppCore.instance()

    logger.info("Checking for internet connection")
    if not check_internet_connection():
        return None
    
    try:
        if app_core.config.update_channel == app_core.config.UpdateChannel.PRE_RELEASE.value:
            release = get_prerelease()
        else:
            release = get_release()

        if not release:
            logger.error("No release version found.")
            raise RuntimeError("No release version found.")

        latest_version:str = release["tag_name"]
        return latest_version, release
    
    except json.JSONDecodeError:
        logger.error("Failed to decode release JSON response.")
        return None

    except req.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        raise RuntimeError(f"Unexpected exception: {e}") from e


def get_platform_assets(assets: ASSETS) -> tuple[UPDATE_ASSET, GUI_LIBRARY_ASSET]:
    """Get the platform update asset and GUI library asset if it was updated.

        Arguments
        ---------
        `assets`: (ASSETS) - The list of assets from the release.

        Returns
        -------
        `tuple[UPDATE_ASSET, GUI_LIBRARY_ASSET|None]`: A tuple containing the update asset and the GUI library asset if it was updated.
    """

    if platform == "win32":
        update_zip_name = WINDOWS_UPDATE_ZIP
        gui_library_zip_name = WINDOWS_GUI_LIBRARY_ZIP
    else:
        update_zip_name = LINUX_UPDATE_ZIP
        gui_library_zip_name = LINUX_GUI_LIBRARY_ZIP

    update_asset:UPDATE_ASSET | None = None
    gui_library_asset:GUI_LIBRARY_ASSET | None = None

    for asset in assets:
        if asset["name"] == update_zip_name:
            update_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
            logger.info(f"Found update asset: {asset['name']} | Size: {asset['size']} | Hash: {asset['digest']}")
        elif asset["name"] == gui_library_zip_name:
            gui_library_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
            logger.info(f"Found GUI library asset: {asset['name']} | Size: {asset['size']} | Hash: {asset['digest']}")

    if not update_asset:
        logger.error(f"No update asset found for {platform} platform.")
        raise RuntimeError(f"No update asset found for {platform} platform.")

    if not gui_library_asset:
        logger.error(f"No GUI library asset found for {platform} platform. Update can't be performed.")
        raise RuntimeError(f"No GUI library asset found for {platform} platform. Update can't be performed.")

    return update_asset, gui_library_asset


def download_update_zip(update_zip_download_url: str, update_zip_download_name: str, update_zip_size: int, attempt:int = 1) -> None:
    """Download the update zip file from the given URL.

        Arguments
        ---------
        `update_zip_download_url`: (str) - The URL to download the update zip file from.

        `update_zip_download_name`: (str) - The name of the update zip file to save.

        `update_zip_size`: (int) - The size of the update zip file in bytes.

        `attempt`: (int) - The current attempt number for downloading the update.
    """

    WindowsRegistry.UpdateProgressWindow.download_label.setText(LanguageStructure.Update.get_translation(2).replace("update_size", str(round(update_zip_size/1024/1024, 2))))
        
    download_response = req.get(update_zip_download_url, stream=True, timeout=15)
    download_response.raise_for_status()

    download_size = 0

    if os.path.exists(UPDATE_DIRECTORY):
        logger.debug("Deleting previous update directory")
        shutil.rmtree(UPDATE_DIRECTORY)
    os.makedirs(UPDATE_DIRECTORY)
    logger.debug("Created update directory")

    logger.info(f"Saving update on disk. Attempt {attempt}")
    with open(f"{UPDATE_DIRECTORY}/{update_zip_download_name}", "wb") as file:
        for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE_FOR_DOWNLOADING):
            download_size += len(chunk)
            file.write(chunk)
            WindowsRegistry.UpdateProgressWindow.download_progress.setValue(int((download_size/update_zip_size)*100))
    logger.info(f"Update saved on disk. Attempt {attempt}")

    with ZipFile(f"{UPDATE_DIRECTORY}/{update_zip_download_name}", "r") as zip_ref:
        zip_ref.extractall(UPDATE_DIRECTORY)
    logger.info(f"Update extracted. Attempt {attempt}")


def download_gui_library_zip(gui_zip_download_url: str, gui_zip_download_name: str, gui_zip_size: int, attempt:int = 1) -> None:
    """Download the GUI library zip file from the given URL.

        Arguments
        ---------
        `gui_zip_download_url`: (str) - The URL to download the GUI library zip file from.

        `gui_zip_download_name`: (str) - The name of the GUI library zip file to save.

        `gui_zip_size`: (int) - The size of the GUI library zip file in bytes.

        `attempt`: (int) - The current attempt number for downloading the GUI library.
    """
    
    download_response = req.get(gui_zip_download_url, stream=True, timeout=15)
    download_response.raise_for_status()

    download_size = 0

    logger.info(f"Saving GUI library on disk. Attempt {attempt}")
    with open(os.path.join(UPDATE_DIRECTORY, "_internal", gui_zip_download_name), "wb") as file:
        for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE_FOR_DOWNLOADING):
            download_size += len(chunk)
            file.write(chunk)
            WindowsRegistry.UpdateProgressWindow.download_progress.setValue(int((download_size/gui_zip_size)*100))
    logger.info(f"GUI library saved on disk. Attempt {attempt}")

    with ZipFile(os.path.join(UPDATE_DIRECTORY, "_internal", gui_zip_download_name), "r") as zip_ref:
        zip_ref.extractall(os.path.join(UPDATE_DIRECTORY, "_internal"))
    logger.info(f"GUI library extracted. Attempt {attempt}")


def download_latest_update(release: RELEASE) -> bool:
    """Download the latest update from GitHub releases.

        Arguments
        ---------
        `release`: (RELEASE) - The release object containing information about the latest release.

        Returns
        -------
        `bool`: True if the download was successful, False otherwise.
    """

    try:
        try:
            assets = release["assets"]
        except KeyError:
            logger.error("No assets found in the latest release.")
            return False

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response.")
            return False

        update_asset, gui_library_asset = get_platform_assets(assets)

        update_zip_download_name, update_zip_download_url, update_zip_size, update_zip_hash = update_asset
        gui_zip_download_name, gui_zip_download_url, gui_zip_size, gui_zip_hash = gui_library_asset
        
        if not (isinstance(update_zip_size, int) and isinstance(update_zip_download_url, str) and isinstance(update_zip_download_name, str) and isinstance(update_zip_hash, str)):
            logger.error(f"""No update found or update is not available for this platform.
                         Update zip size: {update_zip_size},
                         Update zip download URL: {update_zip_download_url},
                         Update zip download name: {update_zip_download_name},
                         Update zip hash: {update_zip_hash}""")
            return False

        if not (isinstance(gui_zip_size, int) and isinstance(gui_zip_download_url, str) and isinstance(gui_zip_download_name, str) and isinstance(gui_zip_hash, str)):
            logger.error(f"""No GUI library found or GUI library is not available for this platform.
                         GUI zip size: {gui_zip_size},
                         GUI zip download URL: {gui_zip_download_url},
                         GUI zip download name: {gui_zip_download_name},
                         GUI zip hash: {gui_zip_hash}""")
            return False

        for attempt in range(1, ATTEMPTS_TO_DOWNLOAD_ZIP+1):
            download_update_zip(update_zip_download_url, update_zip_download_name, update_zip_size, attempt)

            if generate_file_256hash(f"{UPDATE_DIRECTORY}/{update_zip_download_name}") == update_zip_hash:
                logger.info(f"Update zip hash matches: {update_zip_hash}")
                break
            else:
                logger.warning(f"Update zip hash does not match: {update_zip_hash}. Retrying download...")
                if attempt == ATTEMPTS_TO_DOWNLOAD_ZIP:
                    logger.error(f"Failed to download update zip after {ATTEMPTS_TO_DOWNLOAD_ZIP} attempts.")
                    return False
        
        if not os.path.exists(GUI_LIBRARY_DIRECTORY_ZIP):
            logger.debug("GUI library directory zip does not exist. Creating it.")
            compress_directory(GUI_LIBRARY_DIRECTORY, GUI_LIBRARY_DIRECTORY_ZIP)
        
        if generate_file_256hash(GUI_LIBRARY_DIRECTORY_ZIP) != gui_zip_hash:
            logger.warning(f"GUI library zip hash does not match: {gui_zip_hash}. Downloading GUI library zip...")

        for attempt in range(1, ATTEMPTS_TO_DOWNLOAD_ZIP+1):
            download_gui_library_zip(gui_zip_download_url, gui_zip_download_name, gui_zip_size, attempt)

            if generate_file_256hash(os.path.join(UPDATE_DIRECTORY, "_internal", gui_zip_download_name)) == gui_zip_hash:
                logger.info(f"GUI library zip hash matches: {gui_zip_hash}")
                break
            else:
                logger.warning(f"GUI library zip hash does not match: {gui_zip_hash}. Retrying download...")
                if attempt == ATTEMPTS_TO_DOWNLOAD_ZIP:
                    logger.error(f"Failed to download GUI library zip after {ATTEMPTS_TO_DOWNLOAD_ZIP} attempts.")
                    return False

        return True
    
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        return False
