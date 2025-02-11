from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create the async engine
# Make echo=True for logging async_engine!
engine = create_async_engine(settings.DB_URL, echo=settings.DB_DEBUG)

# Create session maker using AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency to get DB session (session will be opened, committed, and closed automatically)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # Yield session for use in routes
        await session.commit()  # Commit transactions after the request
