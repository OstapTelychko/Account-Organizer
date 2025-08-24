

class PrereleaseNotFoundError(Exception):
    """Exception raised when a prerelease is not found."""
    pass


class UpdateAssetNotFoundError(Exception):
    """Exception raised when an update asset is not found in release/prerelease."""
    pass


class GUILibraryAssetNotFoundError(Exception):
    """Exception raised when a GUI asset is not found in release/prerelease."""
    pass
