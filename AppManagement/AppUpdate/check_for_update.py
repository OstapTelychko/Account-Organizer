from PySide6.QtCore import QTimer, QObject, Signal
import threading

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.app_exceptions import FailedToDownloadGUILibraryZipError, FailedToDownloadUpdateZipError

from AppManagement.AppUpdate.download_update import get_latest_version, download_latest_update
from AppManagement.AppUpdate.prepare_update import prepare_update
from AppManagement.AppUpdate.apply_update import apply_update

from AppAnnotations.update_annotations import RELEASE
from languages import LanguageStructure
from project_configuration import ERROR_LOG_FILE

logger = get_logger(__name__)


def update_check_failed(exception: Exception) -> None:
    """Logs error occurred during update check."""
    logger.error(f"Update check failed: {exception}")
    WindowsRegistry.Messages.failed_update_check.exec()


def handle_latest_version(latest_version: tuple[str, RELEASE] | None) -> None:
    """Handle the latest version received from update check."""

    app_core = AppCore.instance()
    if latest_version:
        version, release = latest_version
        if version == app_core.app_version:
            logger.info("No updates available")
            logger.info("__BREAK_LINE__")
            return

        logger.info(f"Latest version: {version} | Current version: {app_core.app_version}")
        failed_download_text = LanguageStructure.Messages.get_translation(35).replace(r"%error_log%", ERROR_LOG_FILE)
        WindowsRegistry.Messages.failed_update_download.setText(failed_download_text)
        WindowsRegistry.Messages.update_available.exec()

        if WindowsRegistry.Messages.update_available.clickedButton() == WindowsRegistry.Messages.update_available.ok_button:
            
            def end_update_with_failure() -> None:
                WindowsRegistry.UpdateProgressWindow.done(1)
                WindowsRegistry.Messages.failed_update_download.exec()

            def _run_update() -> None:
                logger.info("Running update")
                try:
                    if download_latest_update(release):
                        logger.info("Downloaded latest update")
                        prepare_update()
                        apply_update()
                    else:
                        logger.error("Failed to download latest update")
                        end_update_with_failure()
                except FailedToDownloadUpdateZipError:
                    logger.error("Failed to download latest update zip. Closing update window")
                    end_update_with_failure()
                except FailedToDownloadGUILibraryZipError:
                    logger.error("Failed to download latest GUI library zip. Closing update window")
                    end_update_with_failure()

            QTimer.singleShot(150, _run_update)
            WindowsRegistry.UpdateProgressWindow.exec()
    else:
        WindowsRegistry.Messages.failed_update_check.exec()

class UpdateWorker(QObject):
    finished = Signal(object)   # tuple[str, RELEASE] or None
    error = Signal(object)      # Exception

dispatcher = UpdateWorker()  # lives in main (GUI) thread
dispatcher.finished.connect(handle_latest_version)
dispatcher.error.connect(update_check_failed)


def check_for_updates() -> None:
    """Check for updates and ask to download them if available."""

    logger.info("__BREAK_LINE__")
    logger.info("Checking for updates")

    def worker() -> None:
        try:
            latest = get_latest_version()
        except Exception as ex:
            dispatcher.error.emit(ex)
            return
        dispatcher.finished.emit(latest)

    threading.Thread(target=worker, daemon=True).start()
    