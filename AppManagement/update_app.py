import requests as req
import os
import shutil
from sys import platform
from zipfile import ZipFile

from project_configuration import LATEST_RELEASE_URL, UPDATE_DIRECTORY, LINUX_UPDATE_ZIP, WINDOWS_UPDATE_ZIP, GUI_LIBRARY, CURRENT_VERSION_COPY_DIRECTORY, ROOT_DIRECTORY
from AppObjects.session import Session



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
        
        download_response = req.get(download_url, stream=True)
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
    
    except Exception as e:
        print(f"Unexpected exception: {e}")


def prepare_update():
    if os.path.exists(CURRENT_VERSION_COPY_DIRECTORY):
        shutil.rmtree(CURRENT_VERSION_COPY_DIRECTORY)
    # shutil.copytree(os.path.join(ROOT_DIRECTORY, "_internal"), CURRENT_VERSION_COPY_DIRECTORY)
    shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"), os.path.join(CURRENT_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
    
    if platform == "win32":
        shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"), CURRENT_VERSION_COPY_DIRECTORY)
        # shutil.copy2(os.path.join(ROOT_DIRECTORY, "main.exe"), CURRENT_VERSION_COPY_DIRECTORY)
    else:
        shutil.copy2(os.path.join(ROOT_DIRECTORY, "dist", "main", "main"), CURRENT_VERSION_COPY_DIRECTORY)
        # shutil.copy2(os.path.join(ROOT_DIRECTORY, "main"), CURRENT_VERSION_COPY_DIRECTORY)
    
    # shutil.copytree(os.path.join(ROOT_DIRECTORY, "_internal"), CURRENT_VERSION_COPY_DIRECTORY)
    # if not os.path.exists(os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)):
    GUI_LIBRARY_PATH_CURRENT = os.path.join(CURRENT_VERSION_COPY_DIRECTORY, "_internal", GUI_LIBRARY)
    # GUI_LIBRARY_PATH_CURRENT = os.path.join(CURRENT_VERSION_COPY_DIRECTORY,"dist", "main", "_internal", GUI_LIBRARY)
    GUI_LIBRARY_PATH_UPDATE = os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)
    # GUI_LIBRARY_PATH_UPDATE = os.path.join(UPDATE_DIRECTORY, "_internal", GUI_LIBRARY)
    if not os.path.exists(GUI_LIBRARY_PATH_UPDATE):#GUI library is removed from update to reduce size if it already exists it means GUI library was updated
        shutil.copytree(GUI_LIBRARY_PATH_CURRENT, GUI_LIBRARY_PATH_UPDATE)
        


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