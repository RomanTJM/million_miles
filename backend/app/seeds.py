import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.core.security import hash_password
from app.models import User, Base

logger = logging.getLogger(__name__)
settings = get_settings()


async def seed_database():
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),  
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            logger.info("Администратор создан (login: admin, password: admin123)")
        else:
            logger.info("Администратор уже существует")
    
    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_database())
