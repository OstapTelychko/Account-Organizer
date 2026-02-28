import shutil
import os
import sys
import subprocess

from PySide6.QtWidgets import QApplication

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import DEVELOPMENT_MODE, ROOT_DIRECTORY, UPDATE_DIRECTORY, PREVIOUS_VERSION_COPY_DIRECTORY,\
UPDATE_APP_DIRECTORY, UPDATE_BACKUPS_DIRECTORY, MAIN_EXECUTABLE, DEVELOPMENT_ROOT_DIRECTORY,\
DEVELOPMENT_BACKUPS_DIRECTORY, APP_DIRECTORY, BACKUPS_DIRECTORY, PREVIOUS_VERSION_SUFFIX


logger = get_logger(__name__)
SKIP_FILES = {"base_library.zip"}

def mark_current_version_for_deletion(internal_dir: str) -> None:
    """Rename all files/folders in _internal to mark them for deletion on next launch."""
    for root, dirs, files in os.walk(internal_dir, topdown=False):
        for item in files:
            item_path = os.path.join(root, item)
            name, ext = os.path.splitext(item)
            new_name = f"{name}{PREVIOUS_VERSION_SUFFIX}{ext}"
            new_path = os.path.join(root, new_name)

            if item not in SKIP_FILES:
                os.rename(item_path, new_path)
                logger.debug(f"Marked for deletion: {item} -> {new_name}")


def cleanup_previous_version(internal_dir: str) -> None:
    """Removes all files marked as previous version."""
    for root, dirs, files in os.walk(internal_dir, topdown=False):
        for item in files:
            if PREVIOUS_VERSION_SUFFIX in item:
                item_path = os.path.join(root, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            logger.debug(f"Cleaned up previous version file: {item}")


def move_new_version_to_internal(new_internal_dir: str, internal_dir: str) -> None:
    for root, dirs, files in os.walk(new_internal_dir, topdown=False):
        relative_root = os.path.relpath(root, new_internal_dir)
        dest_root = os.path.join(internal_dir, relative_root)
        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            if file in SKIP_FILES:
                continue
            src = os.path.join(root, file)
            dst = os.path.join(dest_root, file)
            os.replace(src, dst)


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
        if sys.platform == "win32":
            logger.debug("Mark current files in _internal for deletion")
            shutil.copytree(APP_DIRECTORY, os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, "_internal"), symlinks=True)
            mark_current_version_for_deletion(APP_DIRECTORY)
            logger.debug("Move new _internal directory to root directory")
            move_new_version_to_internal(UPDATE_APP_DIRECTORY, APP_DIRECTORY)
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
    

    WindowsRegistry.UpdateProgressWindow.apply_update_progress.setValue(4)
    WindowsRegistry.UpdateProgressWindow.done(0)
    WindowsRegistry.MainWindow.raise_()
    WindowsRegistry.MainWindow.activateWindow()
    logger.info("Update applied")

    WindowsRegistry.Messages.update_finished.exec()

    if sys.platform == "win32":
        old_base_library = os.path.normpath(os.path.join(APP_DIRECTORY, "base_library.zip"))
        staged_base_library = os.path.normpath(os.path.join(ROOT_DIRECTORY, "_new_base_library.zip"))
        batch_path = os.path.join(os.path.dirname(APP_DIRECTORY), "_replace_base_library.bat")

        logger.debug(f"Staging base_library.zip from {os.path.join(UPDATE_APP_DIRECTORY, 'base_library.zip')} to {staged_base_library}")
        shutil.copy2(os.path.join(UPDATE_APP_DIRECTORY, "base_library.zip"), staged_base_library)

        logger.debug("Deleting update directory")
        shutil.rmtree(UPDATE_DIRECTORY)
        app_core.end_session()

        batch_content = (
            "@echo off\n"
            "timeout /t 4 /nobreak > NUL 2>&1\n"
            f"del /f /q \"{old_base_library}\"\n"
            f"copy /Y \"{staged_base_library}\" \"{old_base_library}\"\n"
            f"del /f /q \"{staged_base_library}\"\n"
            "REM Cleanup previous version files in _internal\n"
            f"for /r \"{APP_DIRECTORY}\" %%f in (*{PREVIOUS_VERSION_SUFFIX}.*) do (\n"
            "    del /f /q \"%%f\"\n"
            ")\n"
            f"start \"\" \"{sys.executable}\"\n"
            "del \"%~f0\"\n"
        )
        logger.debug(f"Batch content for replacing base_library.zip:\n{batch_content}")

        with open(batch_path, "w") as f:
            f.write(batch_content)

        subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)
        QApplication.quit()
    else:
        logger.debug("Deleting update directory")
        shutil.rmtree(UPDATE_DIRECTORY)
        app_core.restart_app()
