import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models import User
from app.core.security import hash_password


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def setup_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=None,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield async_session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def admin_user(setup_db):
    async_session = setup_db
    
    async with async_session() as session:
        admin = User(
            username="testadmin",
            email="admin@test.com",
            hashed_password=hash_password("testpassword123"),
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        yield admin
