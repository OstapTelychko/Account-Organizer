import shutil
import os

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import DEVELOPMENT_MODE, ROOT_DIRECTORY, UPDATE_DIRECTORY, PREVIOUS_VERSION_COPY_DIRECTORY,\
UPDATE_APP_DIRECTORY, UPDATE_BACKUPS_DIRECTORY, MAIN_EXECUTABLE, DEVELOPMENT_ROOT_DIRECTORY,\
DEVELOPMENT_BACKUPS_DIRECTORY, APP_DIRECTORY, BACKUPS_DIRECTORY

logger = get_logger(__name__)




def apply_update() -> None:
    """Apply the update by moving files and deleting old ones."""

    logger.info("Applying update")
    app_core = AppCore.instance()
    app_core.db.close_connection()

    if DEVELOPMENT_MODE:#if app in development
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(os.path.join(DEVELOPMENT_ROOT_DIRECTORY, "_internal"),
                    os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(UPDATE_APP_DIRECTORY, DEVELOPMENT_ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(DEVELOPMENT_BACKUPS_DIRECTORY)
        logger.debug("Move update backups directory to root directory")
        shutil.move(UPDATE_BACKUPS_DIRECTORY, DEVELOPMENT_ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        shutil.move(os.path.join(DEVELOPMENT_ROOT_DIRECTORY, MAIN_EXECUTABLE), 
                    os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, MAIN_EXECUTABLE))
        shutil.move(os.path.join(UPDATE_DIRECTORY, MAIN_EXECUTABLE),
                    os.path.join(DEVELOPMENT_ROOT_DIRECTORY, MAIN_EXECUTABLE))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(3)

    else:
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(APP_DIRECTORY, os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(UPDATE_APP_DIRECTORY, ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(BACKUPS_DIRECTORY)
        logger.debug("Move update backups directory to root directory")
        shutil.move(UPDATE_BACKUPS_DIRECTORY, ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        shutil.move(os.path.join(ROOT_DIRECTORY, MAIN_EXECUTABLE),
                    os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, MAIN_EXECUTABLE))
        shutil.move(os.path.join(UPDATE_DIRECTORY, MAIN_EXECUTABLE), os.path.join(ROOT_DIRECTORY, MAIN_EXECUTABLE))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(3)
    
    logger.debug("Deleting update directory")
    shutil.rmtree(UPDATE_DIRECTORY)

    WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(4)
    WindowsRegistry.UpdateProgressWindow.done(0)
    WindowsRegistry.MainWindow.raise_()
    WindowsRegistry.MainWindow.activateWindow()
    logger.info("Update applied")

    WindowsRegistry.Messages.update_finished.exec()
    app_core.restart_app()