from unittest.mock import patch, MagicMock, create_autospec
from tests.tests_toolkit import OutOfScopeTestCase
from AppManagement.update_app import check_internet_connection
from requests import Response, head


mocked_head = MagicMock(spec=head)



class TestUpdateApp(OutOfScopeTestCase):
    """Test update application functionality."""

    @patch('AppManagement.update_app.req.head', autospec=True)
    def test_1_internet_connection_check(self, mock_head:MagicMock) -> None:
        """Test internet connection check functionality."""

        mock_head_response = create_autospec(Response, spec_set=True)
        mock_head_response.raise_for_status = MagicMock(return_value=None)
        mock_head.return_value = mock_head_response
        self.assertTrue(check_internet_connection(), "Internet connection check failed although success had been expected")

