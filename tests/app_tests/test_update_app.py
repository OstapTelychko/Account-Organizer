from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, create_autospec, patch

from tests.tests_toolkit import OutOfScopeTestCase
from AppManagement.AppUpdate.download_update import check_internet_connection, get_release
from requests import Response
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects, RequestException, HTTPError

if TYPE_CHECKING:
    from types import FunctionType
    MockedResponse = type("MockedResponse", (MagicMock, Response), {})
    MockedFunction = type("MockedFunction", (MagicMock, FunctionType), {})


class TestUpdateApp(OutOfScopeTestCase):
    """Test update application functionality."""

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
