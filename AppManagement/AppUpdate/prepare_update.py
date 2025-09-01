from __future__ import annotations
from typing import TYPE_CHECKING
import shutil
import os
import concurrent.futures
from sys import platform
from pathlib import Path

from sqlalchemy import create_engine
from alembic import command
from alembic.config import Config

from AppObjects.logger import get_logger
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import PREVIOUS_VERSION_COPY_DIRECTORY, DEVELOPMENT_MODE, ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME,\
GUI_LIBRARY, UPDATE_DIRECTORY, MOVE_FILES_TO_UPDATE_INTERNAL, VERSION_FILE_NAME, ALEMBIC_CONFIG_FILE, \
UPDATE_BACKUPS_DIRECTORY, MOVE_DIRECTORIES_TO_UPDATE_INTERNAL, UPDATE_APP_DIRECTORY, APP_DIRECTORY, BACKUPS_DIRECTORY,\
PREVIOUS_VERSION_BACKUPS_DIRECTORY, GUI_LIBRARY_DIRECTORY, GUI_LIBRARY_UPDATE_PATH

if TYPE_CHECKING:
    from AppObjects.backup import Backup


logger = get_logger(__name__)
path_exists = os.path.exists


def create_single_backup(backup:Backup, app_core:AppCore, update_version:str) -> str:
    """Create a copy of the backup and upgrade it version but doesn't upgrade the database schema."""

    updated_backup_file_path = os.path.join(UPDATE_BACKUPS_DIRECTORY, f"Accounts_{backup.timestamp}_{update_version}.sqlite")
    app_core.db.backup_query.create_backup_based_on_external_db(backup.db_file_path, updated_backup_file_path)
    logger.debug(f"Created backup: {updated_backup_file_path}")
    return updated_backup_file_path


def migrate_single_backup(backup_path:str, app_core:AppCore) -> str:
        """Upgrade the copied backup database schema to the latest version."""

        alembic_config = Config(os.path.join(UPDATE_APP_DIRECTORY, ALEMBIC_CONFIG_FILE))
        alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{backup_path}")
        alembic_config.set_main_option("script_location", os.path.join(UPDATE_APP_DIRECTORY, "alembic"))

        engine = create_engine(f"sqlite:///{backup_path}")
        try:
            if not app_core.db.db_up_to_date(alembic_config, engine):
                command.upgrade(alembic_config, "head")
        finally:
            engine.dispose()
        
        logger.debug(f"Migrated backup: {backup_path}")
        return backup_path


def prepare_update() -> None:
    """Prepare the update by copying the GUI library and creating backups of the database files."""

    logger.info("Preparing update")
    app_core = AppCore.instance()

    if path_exists(PREVIOUS_VERSION_COPY_DIRECTORY):
        shutil.rmtree(PREVIOUS_VERSION_COPY_DIRECTORY)
        logger.info("Deleted previous version copy directory")
    
    logger.debug("Creating previous version copy directory")
    if DEVELOPMENT_MODE:#if app in development
        shutil.copytree(os.path.join(ROOT_DIRECTORY, "dist", "main", BACKUPS_DIRECTORY_NAME),
                        PREVIOUS_VERSION_BACKUPS_DIRECTORY)
    else:
        shutil.copytree(BACKUPS_DIRECTORY, PREVIOUS_VERSION_BACKUPS_DIRECTORY)
    logger.debug("Created previous version copy directory")

    if DEVELOPMENT_MODE:
        gui_library_current_path = os.path.join(ROOT_DIRECTORY, "dist", "main", "_internal", GUI_LIBRARY)
    else:
        gui_library_current_path = GUI_LIBRARY_DIRECTORY

    if not path_exists(GUI_LIBRARY_UPDATE_PATH):#GUI library is removed from update to reduce size of update. If it already exists it means GUI library was updated
        shutil.copytree(gui_library_current_path, GUI_LIBRARY_UPDATE_PATH)
        logger.info("Copied GUI library to update directory")
    
    for file in MOVE_FILES_TO_UPDATE_INTERNAL:
        shutil.copy2(file, UPDATE_APP_DIRECTORY)
        logger.debug(f"Copied file {file} to update directory")
    
    for directory in MOVE_DIRECTORIES_TO_UPDATE_INTERNAL:
        shutil.copytree(directory, os.path.join(UPDATE_APP_DIRECTORY, Path(directory).name))
        logger.debug(f"Copied directory {directory} to update directory")
    
    os.makedirs(UPDATE_BACKUPS_DIRECTORY)
    logger.debug("Created update backups directory")

    if platform == "linux":
        os.chmod(os.path.join(UPDATE_DIRECTORY, "main"), 0o755)#The octal value 0o755 sets these file permissions: • Owner: Read/write/execute • Group: Read/execute • Others: Read/execute
        logger.debug("Changed main file permissions")

    with open(os.path.join(UPDATE_APP_DIRECTORY, VERSION_FILE_NAME)) as version_file:
        update_version = version_file.read()

    WindowsRegistry.UpdateProgressWindow.backups_upgrade_progress.setRange(0, len(app_core.backups))
    upgraded_backups = 0

    logger.info("Creating and migrating backups")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        backup_futures = {
        executor.submit(create_single_backup, backup, app_core, update_version): backup for backup in app_core.backups.values()}
        updated_backups_paths = [future.result() for future in backup_futures]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        path_futures = {
        executor.submit(migrate_single_backup, backup_path, app_core): backup_path for backup_path in updated_backups_paths}
        for future in concurrent.futures.as_completed(path_futures):
            future.result()
            upgraded_backups += 1
            WindowsRegistry.UpdateProgressWindow.backups_upgrade_progress.setValue(upgraded_backups)
    logger.info("Backups created and migrated")
    
    logger.info("Move legacy backups to update directory")
    for backup in app_core.backups.values():
        if not path_exists(os.path.join(UPDATE_BACKUPS_DIRECTORY, Path(backup.db_file_path).name)):
            if DEVELOPMENT_MODE:# I don't want to delete backups in development
                shutil.copy2(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
            else:
                shutil.move(backup.db_file_path, UPDATE_BACKUPS_DIRECTORY)
            logger.debug(f"Moved backup: {backup.db_file_path}")
    
    logger.info("Update preparation finished")