from unittest.mock import MagicMock, create_autospec, patch
from tests.tests_toolkit import OutOfScopeTestCase
from AppManagement.AppUpdate.download_update import check_internet_connection
from requests import Response




class TestUpdateApp(OutOfScopeTestCase):
    """Test update application functionality."""

    @patch('AppManagement.AppUpdate.download_update.req.head', autospec=True)
    def test_1_internet_connection_check(self, mock_head:MagicMock) -> None:
        """Test internet connection check functionality."""


        mock_head_response = create_autospec(Response, spec_set=True)
        mock_head_response.raise_for_status = MagicMock(return_value=None)
        mock_head.return_value = mock_head_response
        self.assertTrue(check_internet_connection(), "Internet connection check failed although success had been expected")

