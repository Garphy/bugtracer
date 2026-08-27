#!/usr/bin/env python3
"""
BugTracer SQLite Database Rolling Backup & Restore CLI Utility.

Usage:
    python scripts/backup_db.py --backup
    python scripts/backup_db.py --list
    python scripts/backup_db.py --restore <backup_file_path>
    python scripts/backup_db.py --prune [--keep 7]
"""

import os
import sys
import argparse

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.config import settings
from backend.app.core.backup import BackupManager

def main():
    parser = argparse.ArgumentParser(description="BugTracer SQLite Database Backup & Restore Tool")
    parser.add_argument("--backup", action="store_true", help="Perform an online hot backup now")
    parser.add_argument("--list", action="store_true", help="List all existing backup files")
    parser.add_argument("--restore", type=str, help="Restore database from specified backup file path or filename")
    parser.add_argument("--prune", action="store_true", help="Prune old backups keeping only the most recent N days")
    parser.add_argument("--keep", type=int, default=settings.BACKUP_KEEP_DAYS, help=f"Number of daily backups to keep (default: {settings.BACKUP_KEEP_DAYS})")

    args = parser.parse_args()

    if not settings.sqlite_db_path:
        print("[Error] Database is not configured as SQLite. Backup tool only supports SQLite.")
        sys.exit(1)

    if args.backup:
        print(f"[*] Source SQLite database: {settings.sqlite_db_path}")
        print(f"[*] Target backup directory: {settings.effective_backup_dir}")
        try:
            target = BackupManager.backup_database(max_keep=args.keep)
            print(f"[SUCCESS] Backup completed successfully: {target}")
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            sys.exit(1)

    elif args.list:
        backups = BackupManager.list_backups()
        print("\n" + "=" * 75)
        print(f"BugTracer SQLite Backups (Directory: {settings.effective_backup_dir})")
        print("=" * 75)
        if not backups:
            print("No backup files found.")
        else:
            print(f"{ 'Filename':<35} | { 'Size':<10} | { 'Created At':<20}")
            print(f"{'-'*35}-+-{'-'*10}-+-{'-'*20}")
            for b in backups:
                print(f"{b['filename']:<35} | {b['size_kb']:>7.2f} KB | {b['created_at']:<20}")
            print(f"\nTotal backups: {len(backups)} (Retention policy: Keep last {args.keep} days)")

    elif args.restore:
        file_path = args.restore
        if not os.path.isabs(file_path) and not os.path.exists(file_path):
            # Check if filename exists inside backup dir
            candidate = os.path.join(settings.effective_backup_dir, file_path)
            if os.path.exists(candidate):
                file_path = candidate

        if not os.path.exists(file_path):
            print(f"[ERROR] Backup file not found: '{args.restore}'")
            sys.exit(1)

        print(f"[!] CAUTION: You are about to restore database from: {file_path}")
        print(f"[!] Target database to be overwritten: {settings.sqlite_db_path}")
        confirm = input("Are you sure you want to proceed with database restore? (yes/N): ")
        if confirm.strip().lower() not in ["y", "yes"]:
            print("Restore operation cancelled by user.")
            sys.exit(0)

        try:
            BackupManager.restore_database(file_path)
            print(f"[SUCCESS] Database successfully restored from '{file_path}'.")
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            sys.exit(1)

    elif args.prune:
        print(f"[*] Pruning backups in '{settings.effective_backup_dir}', keeping most recent {args.keep} files...")
        deleted = BackupManager.prune_backups(max_keep=args.keep)
        if deleted:
            print(f"[SUCCESS] Deleted {len(deleted)} expired backup(s):")
            for d in deleted:
                print(f"  - {os.path.basename(d)}")
        else:
            print("[*] No expired backups to prune.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
