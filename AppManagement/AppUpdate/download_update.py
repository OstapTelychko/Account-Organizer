import json
import os
import shutil
from sys import platform
from zipfile import ZipFile

import requests as req
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry #type: ignore[import-not-found]

from languages import LanguageStructure
from project_configuration import LATEST_RELEASE_URL, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP, UPDATE_DIRECTORY

from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

try:
    from tokens_ssh_gdp_secrets import UPDATE_API_TOKEN#This file is not included in repository. Token have to be provided by user to exceed rate limit of github api
except ImportError:
    UPDATE_API_TOKEN:str|None = None#type: ignore[no-redef]



logger = get_logger(__name__)


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


def get_latest_version() -> str:
    """Get the latest version of the app from GitHub releases.

        Returns
        -------
        `str`: The latest version of the app.
    """

    logger.info("Checking for internet connection")
    if not check_internet_connection():
        return ""
    
    try:
        request_session = requests_retry_session()
        if UPDATE_API_TOKEN:
            response = request_session.get(LATEST_RELEASE_URL, headers={"Authorization": f"token {UPDATE_API_TOKEN}"}, timeout=15)
        else:
            response = request_session.get(LATEST_RELEASE_URL, timeout=15)
        response.raise_for_status()

        latest_version:str = response.json()["tag_name"]
        return latest_version
    
    except req.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return ""


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

        if response.status_code != 200:
            logger.error(f"Failed to get latest release: {response.status_code}")
            return False
        
        try:
            assets = response.json()["assets"]
        except KeyError:
            logger.error("No assets found in the latest release.")
            return False

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response.")
            return False

        total_size = 0
        download_name = ""
        download_url = ""

        for asset in assets:
            if platform == "win32":
                if asset["name"] == WINDOWS_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    download_name = asset["name"]
                    total_size = int(asset["size"])

                    logger.info(f"Starting download of {WINDOWS_UPDATE_ZIP}")
                    logger.debug(f"Download url: {download_url} | Size: {total_size}")
                    break
            else:
                if asset["name"] == LINUX_UPDATE_ZIP:
                    download_url = asset["browser_download_url"]
                    download_name = asset["name"]
                    total_size = int(asset["size"])

                    logger.info(f"Starting download of {LINUX_UPDATE_ZIP}")
                    logger.debug(f"Download url: {download_url} | Size: {total_size}")
                    break
        
        if not (total_size > 0 and isinstance(download_url, str) and download_url.strip() and isinstance(download_name, str) and download_name.strip()):
            logger.error("No update found or update is not available for this platform.")
            return False

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
        with open(f"{UPDATE_DIRECTORY}/{download_name}", "wb") as file:
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                download_size += len(chunk)
                file.write(chunk)
                WindowsRegistry.UpdateProgressWindow.download_progress.setValue(int((download_size/total_size)*100))
        logger.info("Update saved on disk")

        with ZipFile(f"{UPDATE_DIRECTORY}/{download_name}", "r") as zip_ref:
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
