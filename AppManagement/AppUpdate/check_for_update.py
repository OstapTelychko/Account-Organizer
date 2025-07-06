from PySide6.QtCore import QTimer

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger

from AppManagement.AppUpdate.download_update import get_latest_version, download_latest_update
from AppManagement.AppUpdate.prepare_update import prepare_update
from AppManagement.AppUpdate.apply_update import apply_update

logger = get_logger(__name__)



def check_for_updates() -> None:
    """Check for updates and ask to download them if available."""

    logger.info("__BREAK_LINE__")
    logger.info("Checking for updates")
    app_core = AppCore.instance()
    latest_version = get_latest_version()

    if latest_version:
        version, release = latest_version
        if version == app_core.app_version:
            logger.info("No updates available")
            logger.info("__BREAK_LINE__")
            return

        logger.info(f"Latest version: {version} | Current version: {app_core.app_version}")
        WindowsRegistry.Messages.update_available.exec()
        if WindowsRegistry.Messages.update_available.clickedButton() == WindowsRegistry.Messages.update_available.ok_button:
            
            def _run_update() -> None:
                logger.info("Running update")
                if download_latest_update(release):
                    logger.info("Downloaded latest update")
                    prepare_update()
                    apply_update()
                else:
                    logger.error("Failed to download latest update")
                    WindowsRegistry.UpdateProgressWindow.done(1)
                    

            QTimer.singleShot(150, _run_update)
            WindowsRegistry.UpdateProgressWindow.exec()
    else:
        WindowsRegistry.Messages.failed_update_check.exec()