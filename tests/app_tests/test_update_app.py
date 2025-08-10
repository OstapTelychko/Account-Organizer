from unittest.mock import MagicMock, create_autospec, patch
from tests.tests_toolkit import OutOfScopeTestCase
from AppManagement.AppUpdate.download_update import check_internet_connection
from requests import Response
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects, RequestException




class TestUpdateApp(OutOfScopeTestCase):
    """Test update application functionality."""

    @patch('AppManagement.AppUpdate.download_update.req.head', autospec=True)
    def test_1_internet_connection_check(self, mock_head:MagicMock) -> None:
        """Test internet connection check functionality based on different response scenarios."""

        mock_successful_head_response = create_autospec(Response, spec_set=True)
        mock_successful_head_response.raise_for_status = MagicMock(return_value=None)
        mock_head.return_value = mock_successful_head_response
        self.assertTrue(check_internet_connection(), "Internet connection check failed although success had been expected")

        mock_timeout_head_response = create_autospec(Response, spec_set=True)
        mock_timeout_head_response.raise_for_status = MagicMock(side_effect=Timeout)
        mock_head.return_value = mock_timeout_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by timeout")

        mock_connection_error_head_response = create_autospec(Response, spec_set=True)
        mock_connection_error_head_response.raise_for_status = MagicMock(side_effect=ConnectionError)
        mock_head.return_value = mock_connection_error_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by connection error")

        mock_too_many_redirects_head_response = create_autospec(Response, spec_set=True)
        mock_too_many_redirects_head_response.raise_for_status = MagicMock(side_effect=TooManyRedirects)
        mock_head.return_value = mock_too_many_redirects_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by too many redirects")

        mock_request_exception_head_response = create_autospec(Response, spec_set=True)
        mock_request_exception_head_response.raise_for_status = MagicMock(side_effect=RequestException)
        mock_head.return_value = mock_request_exception_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by request exception")

        mock_runtime_error_head_response = create_autospec(Response, spec_set=True)
        mock_runtime_error_head_response.raise_for_status = MagicMock(side_effect=RuntimeError)
        mock_head.return_value = mock_runtime_error_head_response
        self.assertFalse(check_internet_connection(), "Internet connection check passed although failure was expected caused by runtime error")
    

    @patch('AppManagement.AppUpdate.download_update.req.Session.get', autospec=True)
    def test_2_get_release(self, mock_get:MagicMock) -> None:
        """Test get release functionality based on different response scenarios."""

        # mock_

