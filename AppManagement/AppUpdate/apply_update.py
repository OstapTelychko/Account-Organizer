import shutil
import os
from sys import platform

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import DEVELOPMENT_MODE, ROOT_DIRECTORY, UPDATE_DIRECTORY, PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME

logger = get_logger(__name__)




def apply_update() -> None:
    """Apply the update by moving files and deleting old ones."""

    logger.info("Applying update")
    app_core = AppCore.instance()
    app_core.db.close_connection()

    if DEVELOPMENT_MODE:#if app in development
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), os.path.join(ROOT_DIRECTORY, "dist", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME))
        logger.debug("Move update backups directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), os.path.join(ROOT_DIRECTORY, "dist", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        if platform == "win32":
            shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main.exe"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main.exe"))
        else:
            shutil.move(os.path.join(ROOT_DIRECTORY, "dist", "main", "main"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "dist", "main", "main"))
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(3)

    else:
        logger.debug("Move old _internal directory to previous version copy directory")
        shutil.move(os.path.join(ROOT_DIRECTORY, "_internal"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"))
        logger.debug("Move new _internal directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, "_internal"), ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(1)

        logger.debug("Deleting backups directory")
        shutil.rmtree(os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME))
        logger.debug("Move update backups directory to root directory")
        shutil.move(os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME), ROOT_DIRECTORY)
        WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(2)

        logger.debug("Move main file to root directory")
        if platform == "win32":
            shutil.move(os.path.join(ROOT_DIRECTORY, "main.exe"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main.exe"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main.exe"), os.path.join(ROOT_DIRECTORY, "main.exe"))
        else:
            shutil.move(os.path.join(ROOT_DIRECTORY, "main"), os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "main"))
            shutil.move(os.path.join(UPDATE_DIRECTORY, "main"), os.path.join(ROOT_DIRECTORY, "main"))
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