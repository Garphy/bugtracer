import os
import asyncio
import tempfile
import sqlite3
import pytest
from datetime import datetime
from backend.app.core.backup import BackupManager
from backend.app.core.database import AsyncSessionLocal
from backend.app.services.bug_service import BugService
from backend.app.schemas.bug import BugCreate
from backend.app.models.user import User
from sqlalchemy import select, text

@pytest.mark.asyncio
async def test_sqlite_wal_and_pragmas():
    """Verify that SQLite WAL mode and busy timeout are active."""
    async with AsyncSessionLocal() as session:
        # Check journal_mode
        res = await session.execute(text("PRAGMA journal_mode;"))
        journal_mode = res.scalar_one().lower()
        assert journal_mode in ["wal", "memory"], f"Expected WAL mode, got {journal_mode}"

        # Check busy_timeout
        res = await session.execute(text("PRAGMA busy_timeout;"))
        busy_timeout = res.scalar_one()
        assert busy_timeout >= 5000, f"Expected busy_timeout >= 5000, got {busy_timeout}"

@pytest.mark.asyncio
async def test_high_concurrency_writes_and_reads():
    """Verify that heavy concurrent writes and reads succeed under WAL mode without locks."""
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).limit(1))
        user = user_res.scalars().first()
        assert user is not None

    async def write_bug(idx: int):
        async with AsyncSessionLocal() as session:
            bug_in = BugCreate(
                project_id=1,
                content=f"Concurrent stress test write payload #{idx}",
                ver="2.0.0",
                status=1
            )
            created = await BugService.create_bug(session, bug_in, user)
            return created.id

    async def read_bugs():
        async with AsyncSessionLocal() as session:
            res = await BugService.list_bugs(session, project_id=1, page=1, page_size=50)
            return res["total"]

    # Concurrently fire 20 write tasks and 20 read tasks
    write_tasks = [write_bug(i) for i in range(20)]
    read_tasks = [read_bugs() for _ in range(20)]

    results = await asyncio.gather(*write_tasks, *read_tasks, return_exceptions=False)
    assert len(results) == 40
    # All 20 write tasks returned valid integer IDs
    created_ids = results[:20]
    assert all(isinstance(bid, int) for bid in created_ids)

def test_backup_manager_rolling_retention_and_restore():
    """Test BackupManager backup creation, 7-day rolling pruning, and restore consistency."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_source.db")
        backup_dir = os.path.join(temp_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # 1. Create a dummy sqlite database with some data
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);")
        conn.execute("INSERT INTO items (name) VALUES ('Alpha'), ('Beta'), ('Gamma');")
        conn.commit()
        conn.close()

        # 2. Perform hot backup
        backup_file = BackupManager.backup_database(
            source_db_path=db_path,
            backup_dir=backup_dir,
            max_keep=7
        )
        assert backup_file is not None
        assert os.path.exists(backup_file)

        # 3. Simulate creating 10 daily backups
        for i in range(10):
            fake_filename = f"bugtracer_202608{10+i:02d}_120000.db"
            fake_path = os.path.join(backup_dir, fake_filename)
            with open(fake_path, "wb") as f_out:
                f_out.write(b"fake sqlite header")
            # Set artificial modification times
            mtime = datetime.now().timestamp() - (10 - i) * 86400
            os.utime(fake_path, (mtime, mtime))

        # 4. Prune keeping only 7
        deleted = BackupManager.prune_backups(backup_dir=backup_dir, max_keep=7)
        remaining = BackupManager.list_backups(backup_dir=backup_dir)

        assert len(remaining) == 7
        assert len(deleted) > 0

        # 5. Test restore to a new database location
        restored_db_path = os.path.join(temp_dir, "restored.db")
        success = BackupManager.restore_database(backup_file, target_db_path=restored_db_path)
        assert success is True
        assert os.path.exists(restored_db_path)

        # Verify data inside restored database
        r_conn = sqlite3.connect(restored_db_path)
        rows = r_conn.execute("SELECT name FROM items ORDER BY id;").fetchall()
        r_conn.close()
        assert [r[0] for r in rows] == ["Alpha", "Beta", "Gamma"]
