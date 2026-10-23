

class PrereleaseNotFoundError(Exception):
    """Exception raised when a prerelease is not found."""
    pass


class UpdateAssetNotFoundError(Exception):
    """Exception raised when an update asset is not found in release/prerelease."""
    pass


class GUILibraryAssetNotFoundError(Exception):
    """Exception raised when a GUI asset is not found in release/prerelease."""
    pass


class FailedToDownloadUpdateZipError(Exception):
    """Exception raised when the update zip file failed to download."""
    pass


class FailedToDownloadGUILibraryZipError(Exception):
    """Exception raised when the GUI library zip file failed to download."""
    pass


class WidgetIsDisabledError(Exception):
    """Exception raised when a widget is disabled."""
    pass


class WidgetIsNotVisibleError(Exception):
    """Exception raised when a widget is not visible."""
    pass


class ReminderValidationError(Exception):
    """Exception raised when monthly reminder data is invalid. `reason` holds one of the class constants."""

    NAME_TOO_SHORT = "name_too_short"
    NAME_EXISTS = "name_exists"
    NO_CATEGORY = "no_category"
    DAY_OUT_OF_RANGE = "day_out_of_range"

    def __init__(self, reason:str) -> None:
        super().__init__(reason)
        self.reason = reason