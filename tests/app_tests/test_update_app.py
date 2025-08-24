from __future__ import annotations
import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, create_autospec, mock_open, patch
from io import BytesIO
from zipfile import ZipFile
from requests import Response
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects, RequestException, HTTPError

from tests.tests_toolkit import OutOfScopeTestCase
from AppObjects.app_exceptions import PrereleaseNotFoundError, UpdateAssetNotFoundError, GUILibraryAssetNotFoundError
from AppManagement.AppUpdate.download_update import check_internet_connection, get_release, get_prerelease, get_platform_assets, download_update_zip
from project_configuration import WINDOWS_GUI_LIBRARY_ZIP, WINDOWS_UPDATE_ZIP, LINUX_GUI_LIBRARY_ZIP, LINUX_UPDATE_ZIP, TEST_UPDATE_DIRECTORY

if TYPE_CHECKING:
    from types import FunctionType
    MockedResponse = type("MockedResponse", (MagicMock, Response), {})
    MockedFunction = type("MockedFunction", (MagicMock, FunctionType), {})
    MockedVariable = type("MockedVariable", (MagicMock, bool, str, int, float, dict, set, list, tuple), {})
    MockedZipFile = type("MockedZipFile", (MagicMock, ZipFile), {})


class TestUpdateApp(OutOfScopeTestCase):
    """Test update application functionality."""

    def setUp(self) -> None:
        self.test_assets = [
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274696711",
                "id": 274696711,
                "node_id": "RA_kwDOJXgXOs4QX4oH",
                "name": "Account_Organizer_linux_setup.zip",
                "label": None,
                "content_type": "application/zip",
                "state": "uploaded",
                "size": 96293136,
                "digest": "sha256:4e93c86b14c42ba5d3886bfad190218292139ebc89a51d9bc7d3272878b5bf6d",
                "download_count": 0,
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/Account_Organizer_linux_setup.zip"
            },
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274691163",
                "id": 274691163,
                "node_id": "RA_kwDOJXgXOs4QX3Rb",
                "name": "Account_Organizer_windows_setup.exe",
                "label": None,
                "content_type": "application/x-msdownload",
                "state": "uploaded",
                "size": 41629268,
                "digest": "sha256:fbc0f9780b28b5a71be27c8b7b014c1686c50f36d98a8b66aa0de0b12cb043e7",
                "download_count": 0,
                "created_at": "2025-07-20T20:46:00Z",
                "updated_at": "2025-07-20T20:46:37Z",
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/Account_Organizer_windows_setup.exe"
            },
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274696809",
                "id": 274696809,
                "node_id": "RA_kwDOJXgXOs4QX4pp",
                "name": "Linux_PySide6.zip",
                "label": None,
                "content_type": "application/zip",
                "state": "uploaded",
                "size": 35896621,
                "digest": "sha256:bbebb29206a6fc2b4c2a85de6e39db620e8f8cd4b1cef424ce42bf5514209508",
                "download_count": 0,
                "created_at": "2025-07-20T21:18:17Z",
                "updated_at": "2025-07-20T21:18:29Z",
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/Linux_PySide6.zip"
            },
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274696845",
                "id": 274696845,
                "node_id": "RA_kwDOJXgXOs4QX4qN",
                "name": "linux_update.zip",
                "label": None,
                "content_type": "application/zip",
                "state": "uploaded",
                "size": 31736222,
                "digest": "sha256:5a0aa96334f39cf491fd7e70568fb3683e09b8c7c90f37c8e3353d3b116d4b74",
                "download_count": 1,
                "created_at": "2025-07-20T21:18:31Z",
                "updated_at": "2025-07-20T21:18:41Z",
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/linux_update.zip"
            },
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274691375",
                "id": 274691375,
                "node_id": "RA_kwDOJXgXOs4QX3Uv",
                "name": "Windows_PySide6.zip",
                "label": None,
                "content_type": "application/x-zip-compressed",
                "state": "uploaded",
                "size": 19077069,
                "digest": "sha256:32f2caa35c3402171694c0bb95897bf17938d68c9c2044c402ebf46384534a85",
                "download_count": 0,
                "created_at": "2025-07-20T20:46:48Z",
                "updated_at": "2025-07-20T20:47:19Z",
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/Windows_PySide6.zip"
            },
            {
                "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/assets/274692877",
                "id": 274692877,
                "node_id": "RA_kwDOJXgXOs4QX3sN",
                "name": "windows_update.zip",
                "label": None,
                "content_type": "application/x-zip-compressed",
                "state": "uploaded",
                "size": 15514847,
                "digest": "sha256:ea77316bb4c57caaed9a5473875f49f397a964a5ea32087914a746b91f097568",
                "download_count": 1,
                "created_at": "2025-07-20T20:58:45Z",
                "updated_at": "2025-07-20T20:59:06Z",
                "browser_download_url": "https://github.com/OstapTelychko/Account-Organizer/releases/download/1.2.1/windows_update.zip"
            }
        ]
            
        self.test_release = {
            "url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/228638431",
            "assets_url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/releases/228638431/assets",
            "upload_url": "https://uploads.github.com/repos/OstapTelychko/Account-Organizer/releases/228638431/assets{?name,label}",
            "html_url": "https://github.com/OstapTelychko/Account-Organizer/releases/tag/1.2.1",
            "id": 228638431,
            "node_id": "RE_kwDOJXgXOs4NoL7f",
            "tag_name": "1.2.1",
            "target_commitish": "master",
            "name": "1.2.1",
            "draft": False,
            "immutable": False,
            "prerelease": False,
            "assets": self.test_assets,
            "tarball_url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/tarball/1.2.1",
            "zipball_url": "https://api.github.com/repos/OstapTelychko/Account-Organizer/zipball/1.2.1",
        }

        super().setUp()



    @patch('AppManagement.AppUpdate.download_update.req.head', autospec=True)
    def test_1_internet_connection_check(self, mock_head:MockedFunction) -> None:
        """Test internet connection check functionality based on different response scenarios."""
        
        mock_successful_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_successful_head_response.raise_for_status = MagicMock(return_value=None)
        mock_head.return_value = mock_successful_head_response
        self.assertTrue(check_internet_connection(), "Internet connection check failed although success had been expected")

        mock_timeout_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_timeout_head_response.raise_for_status = MagicMock(side_effect=Timeout)
        mock_head.return_value = mock_timeout_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by timeout")

        mock_connection_error_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_connection_error_head_response.raise_for_status = MagicMock(side_effect=ConnectionError)
        mock_head.return_value = mock_connection_error_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by connection error")

        mock_too_many_redirects_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_too_many_redirects_head_response.raise_for_status = MagicMock(side_effect=TooManyRedirects)
        mock_head.return_value = mock_too_many_redirects_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by too many redirects")

        mock_request_exception_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_request_exception_head_response.raise_for_status = MagicMock(side_effect=RequestException)
        mock_head.return_value = mock_request_exception_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by request exception")

        mock_runtime_error_head_response:MockedResponse = create_autospec(Response, spec_set=True)
        mock_runtime_error_head_response.raise_for_status = MagicMock(side_effect=RuntimeError)
        mock_head.return_value = mock_runtime_error_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by runtime error")
    

    @patch('AppManagement.AppUpdate.download_update.req.Session.get', autospec=True)
    def test_2_get_release(self, mock_get:MockedFunction) -> None:
        """Test get release functionality based on different response scenarios."""

        mock_successful_get_response:MockedResponse = create_autospec(Response)
        type(mock_successful_get_response).status_code = PropertyMock(return_value=200)
        mock_successful_get_response.raise_for_status = MagicMock(return_value=None)
        expected_result = {"Release data": "Hello world"}
        mock_successful_get_response.json = MagicMock(return_value=expected_result)
        mock_get.return_value = mock_successful_get_response

        result = get_release()
        self.assertEqual(result, expected_result, f"Failed to get expected release data. Expected: {expected_result}, Got: {result}")

        mock_wrong_status_code_get_response:MockedResponse = create_autospec(Response)
        type(mock_wrong_status_code_get_response).status_code = PropertyMock(return_value=404)
        mock_wrong_status_code_get_response.raise_for_status = MagicMock(return_value=None, side_effect=None)
        mock_get.return_value = mock_wrong_status_code_get_response
        with self.assertRaises(HTTPError, msg="Get release didn't raised HTTPError as expected for status code other then 200"):
            get_release()


    @patch('AppManagement.AppUpdate.download_update.req.Session.get', autospec=True)
    def test_3_get_prerelease(self, mock_get:MockedFunction) -> None:
        """Test get prerelease functionality based on different response scenarios."""

        mock_successful_get_response:MockedResponse = create_autospec(Response)
        type(mock_successful_get_response).status_code = PropertyMock(return_value=200)
        mock_successful_get_response.raise_for_status = MagicMock(return_value=None)
        mock_successful_get_response.json = MagicMock(return_value=[{"prerelease": "Hello"}, {"release": "World"}])
        mock_get.return_value = mock_successful_get_response

        expected_result = {"prerelease": "Hello"}
        result = get_prerelease()
        self.assertEqual(result, expected_result, f"Failed to get expected prerelease data. Expected: {expected_result}, Got: {result}")

        mock_wrong_status_code_get_response:MockedResponse = create_autospec(Response)
        type(mock_wrong_status_code_get_response).status_code = PropertyMock(return_value=404)
        mock_wrong_status_code_get_response.raise_for_status = MagicMock(return_value=None, side_effect=None)
        mock_get.return_value = mock_wrong_status_code_get_response
        with self.assertRaises(HTTPError, msg="Get prerelease didn't raised HTTPError as expected for status code other then 200"):
            get_prerelease()

        mock_get_response_without_prerelease:MockedResponse = create_autospec(Response)
        type(mock_get_response_without_prerelease).status_code = PropertyMock(return_value=200)
        mock_get_response_without_prerelease.raise_for_status = MagicMock(return_value=None)
        mock_get_response_without_prerelease.json = MagicMock(return_value=[{"release": "Hello"}, {"release": "World"}])
        mock_get.return_value = mock_get_response_without_prerelease

        with self.assertRaises(PrereleaseNotFoundError,
            msg="Get prerelease didn't raised PrereleaseNotFoundError as expected for response without prerelease data"):
            get_prerelease()


    @patch("AppManagement.AppUpdate.download_update.platform", new="win32")
    def test_4_get_platform_assets_windows(self) -> None:
        """Test get platform assets from release for Windows platform."""

        #Remove linux assets
        for asset in self.test_assets.copy():
            if "linux" in asset["name"].lower():
                self.test_assets.remove(asset)
        
        update_zip_asset = None
        gui_library_asset = None
        for asset in self.test_assets:
            if asset["name"] == WINDOWS_UPDATE_ZIP:
                update_zip_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
            elif asset["name"] == WINDOWS_GUI_LIBRARY_ZIP:
                gui_library_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
        self.assertIsNotNone(update_zip_asset, f"Test update asset {WINDOWS_UPDATE_ZIP} not found in test assets.")
        self.assertIsNotNone(gui_library_asset, f"Test GUI library asset {WINDOWS_GUI_LIBRARY_ZIP} not found in test assets.")

        self.assertEqual((update_zip_asset, gui_library_asset), get_platform_assets(self.test_assets), "Failed to get platform assets for Windows.")

        with self.assertRaises(UpdateAssetNotFoundError, msg="Update asset not found error not raised as expected for platform windows"):
            get_platform_assets([{"name":""}])
        
        for asset in self.test_assets.copy():
            if asset["name"] == WINDOWS_GUI_LIBRARY_ZIP:
                self.test_assets.remove(asset)
        with self.assertRaises(GUILibraryAssetNotFoundError, msg="GUI library asset not found error not raised as expected for platform windows"):
            get_platform_assets(self.test_assets)
    

    @patch("AppManagement.AppUpdate.download_update.platform", new="linux")
    def test_5_get_platform_assets_linux(self) -> None:
        """Test get platform assets from release for Linux platform."""

        # Remove windows assets
        for asset in self.test_assets.copy():
            if "win" in asset["name"].lower():
                self.test_assets.remove(asset)

        update_zip_asset = None
        gui_library_asset = None
        for asset in self.test_assets:
            if asset["name"] == LINUX_UPDATE_ZIP:
                update_zip_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
            elif asset["name"] == LINUX_GUI_LIBRARY_ZIP:
                gui_library_asset = (asset["name"], asset["browser_download_url"], asset["size"], asset["digest"])
        self.assertIsNotNone(update_zip_asset, f"Test update asset {LINUX_UPDATE_ZIP} not found in test assets.")
        self.assertIsNotNone(gui_library_asset, f"Test GUI library asset {LINUX_GUI_LIBRARY_ZIP} not found in test assets.")

        self.assertEqual((update_zip_asset, gui_library_asset), get_platform_assets(self.test_assets), "Failed to get platform assets for Linux.")

        with self.assertRaises(UpdateAssetNotFoundError, msg="Update asset not found error not raised as expected for platform linux"):
            get_platform_assets([{"name":""}])

        for asset in self.test_assets.copy():
            if asset["name"] == LINUX_GUI_LIBRARY_ZIP:
                self.test_assets.remove(asset)
        with self.assertRaises(GUILibraryAssetNotFoundError, msg="GUI library asset not found error not raised as expected for platform linux"):
            get_platform_assets(self.test_assets)
    
    
    @patch("AppManagement.AppUpdate.download_update.UPDATE_DIRECTORY", new=TEST_UPDATE_DIRECTORY)
    @patch('AppManagement.AppUpdate.download_update.ZipFile', autospec=True)
    @patch('AppManagement.AppUpdate.download_update.req.get', autospec=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_6_download_update_zip(self, mock_open:MockedFunction, mock_get:MockedFunction, mock_zipfile:MockedZipFile):
        """Test download update zip is downloaded and saved correctly"""

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("test.txt", "test content")
        test_zip_content = zip_buffer.getvalue()

        mock_successful_response:MockedResponse = create_autospec(Response)
        mock_successful_response.status_code = 200
        mock_successful_response.iter_content = MagicMock(return_value=iter([test_zip_content]))
        mock_successful_response.raise_for_status = MagicMock(return_value=None)
        mock_get.return_value = mock_successful_response

        update_zip_download_name = ""
        update_zip_download_url = ""
        update_zip_size = 0
        for asset in self.test_assets:
            if asset["name"] == LINUX_UPDATE_ZIP:
                update_zip_download_name:str = asset["name"]
                update_zip_download_url:str = asset["browser_download_url"]
                update_zip_size:int = asset["size"]
        self.assertNotEqual("", update_zip_download_name, f"Test update asset {LINUX_UPDATE_ZIP} not found in test assets.")

        mock_zip_file_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_file_instance

        download_update_zip(update_zip_download_url, update_zip_download_name, update_zip_size, 0)

        mock_get.assert_called_once_with(update_zip_download_url, stream=True, timeout=15)
        mock_open.assert_called_once_with(os.path.join(TEST_UPDATE_DIRECTORY, update_zip_download_name), 'wb')

        handle:MockedFunction = mock_open()
        handle.write.assert_called_once_with(test_zip_content)

        mock_zipfile.assert_called_once_with(os.path.join(TEST_UPDATE_DIRECTORY, update_zip_download_name), 'r')
        mock_zip_file_instance.extractall.assert_called_once_with(TEST_UPDATE_DIRECTORY)
