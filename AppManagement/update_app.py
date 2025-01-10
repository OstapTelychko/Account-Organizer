import requests as req

from project_configuration import LATEST_RELEASE_URL, VERSION_FILE_NAME
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


def check_for_updates():
    latest_version = get_latest_version()
    if latest_version:
        if latest_version != Session.app_version:
            return latest_version
        else:
            return "No updates available."
    else:
        return "Failed to check for updates."