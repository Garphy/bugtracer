import os
import glob
import sqlite3
import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages SQLite online hot backups, rolling retention (default 7 days), and restore."""

    @classmethod
    def get_source_db_path(cls) -> Optional[str]:
        return settings.sqlite_db_path

    @classmethod
    def get_backup_dir(cls) -> str:
        backup_dir = settings.effective_backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    @classmethod
    def backup_database(
        cls,
        source_db_path: Optional[str] = None,
        backup_dir: Optional[str] = None,
        max_keep: Optional[int] = None
    ) -> Optional[str]:
        """
        Performs an online safe hot backup of SQLite database using sqlite3.Connection.backup().
        Works reliably under WAL mode without locking or taking down the active database.
        """
        source = source_db_path or cls.get_source_db_path()
        if not source or not os.path.exists(source):
            logger.warning(f"Cannot perform SQLite backup: Source database file not found at '{source}'.")
            return None

        target_dir = backup_dir or cls.get_backup_dir()
        os.makedirs(target_dir, exist_ok=True)

        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        target_filename = f"bugtracer_{timestamp_str}.db"
        target_filepath = os.path.join(target_dir, target_filename)

        logger.info(f"Starting online hot backup from '{source}' to '{target_filepath}'...")
        try:
            source_conn = sqlite3.connect(source)
            target_conn = sqlite3.connect(target_filepath)

            with target_conn:
                source_conn.backup(target_conn, pages=100, sleep=0.01)

            source_conn.close()
            target_conn.close()

            file_size_kb = round(os.path.getsize(target_filepath) / 1024, 2)
            logger.info(f"Database backup succeeded: '{target_filepath}' ({file_size_kb} KB)")

            keep_count = max_keep if max_keep is not None else settings.BACKUP_KEEP_DAYS
            cls.prune_backups(target_dir, max_keep=keep_count)

            return target_filepath
        except Exception as e:
            logger.error(f"Database backup failed: {e}", exc_info=True)
            if os.path.exists(target_filepath):
                try:
                    os.remove(target_filepath)
                except OSError:
                    pass
            raise

    @classmethod
    def prune_backups(cls, backup_dir: Optional[str] = None, max_keep: int = 7) -> List[str]:
        """
        Scans the backup directory, keeps the latest  backups, and removes older ones.
        """
        target_dir = backup_dir or cls.get_backup_dir()
        pattern = os.path.join(target_dir, "bugtracer_*.db")
        backup_files = glob.glob(pattern)

        valid_files = [f for f in backup_files if not f.endswith("-wal") and not f.endswith("-shm")]
        valid_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

        deleted = []
        if len(valid_files) > max_keep:
            for old_file in valid_files[max_keep:]:
                try:
                    os.remove(old_file)
                    deleted.append(old_file)
                    logger.info(f"Pruned expired backup file: '{old_file}'")
                except OSError as e:
                    logger.warning(f"Failed to remove expired backup '{old_file}': {e}")

        return deleted

    @classmethod
    def list_backups(cls, backup_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of all backup files sorted by creation time descending.
        """
        target_dir = backup_dir or cls.get_backup_dir()
        pattern = os.path.join(target_dir, "bugtracer_*.db")
        backup_files = [f for f in glob.glob(pattern) if not f.endswith("-wal") and not f.endswith("-shm")]
        backup_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

        results = []
        for path in backup_files:
            stat = os.stat(path)
            results.append({
                "filename": os.path.basename(path),
                "filepath": path,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": stat.st_mtime
            })
        return results

    @classmethod
    def restore_database(cls, backup_file_path: str, target_db_path: Optional[str] = None) -> bool:
        """
        Safely restores a backup file into the target database location.
        """
        if not os.path.exists(backup_file_path):
            raise FileNotFoundError(f"Backup file not found: '{backup_file_path}'")

        target = target_db_path or cls.get_source_db_path()
        if not target:
            raise ValueError("Target database path could not be resolved.")

        logger.info(f"Restoring database from '{backup_file_path}' to '{target}'...")
        source_conn = sqlite3.connect(backup_file_path)
        target_conn = sqlite3.connect(target)

        try:
            with target_conn:
                source_conn.backup(target_conn)
            logger.info(f"Database successfully restored to '{target}'.")
            return True
        finally:
            source_conn.close()
            target_conn.close()

# Background Scheduler Task
_scheduler_task: Optional[asyncio.Task] = None

async def _backup_loop():
    """Background async loop for daily scheduled rolling backups."""
    logger.info("Database backup scheduler background worker started.")

    try:
        backups = BackupManager.list_backups()
        today_prefix = datetime.now().strftime("bugtracer_%Y%m%d")
        has_today_backup = any(b["filename"].startswith(today_prefix) for b in backups)
        if not has_today_backup:
            logger.info("No backup found for today. Creating initial daily backup on service startup...")
            BackupManager.backup_database()
    except Exception as e:
        logger.warning(f"Startup initial backup check encountered an issue: {e}")

    while True:
        try:
            now = datetime.now()
            target_time = datetime.combine(now.date(), time(hour=settings.BACKUP_HOUR, minute=0, second=0))
            if target_time <= now:
                target_time += timedelta(days=1)

            wait_seconds = (target_time - now).total_seconds()
            logger.info(f"Next automated database backup scheduled in {round(wait_seconds / 3600, 2)} hours (at {target_time}).")

            await asyncio.sleep(wait_seconds)

            logger.info("Executing scheduled daily database backup...")
            BackupManager.backup_database()
        except asyncio.CancelledError:
            logger.info("Database backup scheduler loop received cancellation.")
            break
        except Exception as e:
            logger.error(f"Error in database backup scheduler loop: {e}", exc_info=True)
            await asyncio.sleep(600)

def start_backup_scheduler():
    global _scheduler_task
    if not settings.BACKUP_ENABLED:
        logger.info("Database backup scheduler is disabled in settings.")
        return

    if not settings.sqlite_db_path:
        logger.info("Database is not SQLite. Background SQLite backup scheduler will not start.")
        return

    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_backup_loop())
        logger.info("Database backup scheduler background task created.")

def stop_backup_scheduler():
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        _scheduler_task = None
        logger.info("Database backup scheduler background task stopped.")
