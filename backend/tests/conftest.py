import os
import tempfile
import pytest
from backend.app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensures tests run on an isolated temporary SQLite database."""
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_bugtracer.db")
    orig_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{test_db_path}"
    
    # Re-initialize engine with test database URL
    from backend.app.core import database
    database.engine = database.create_async_engine(
        settings.effective_database_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )
    database.AsyncSessionLocal = database.async_sessionmaker(
        bind=database.engine,
        class_=database.AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    yield
    
    # Teardown
    settings.DATABASE_URL = orig_db_url
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass
