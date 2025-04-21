import asyncio
import pickle

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import patch, AsyncMock

from main import app
from src.database.models import Base, User, UserRole
from src.database.db import get_db
from src.services.auth import create_access_token, Hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "user",
    "email": "user@example.com",
    "password": "12345678",
}

test_admin_user = User(
    id=1,
    username="admin",
    email="admin@example.com",
    avatar="https://twitter.com/gravatar",
    role=UserRole.ADMIN,
    confirmed=True,
)


class MockRedis:
    """Mock Redis client for testing."""
    def __init__(self, *args, **kwargs):
        self._cache = {}
        self.decode_responses = kwargs.get('decode_responses', True)

    async def get(self, key):
        value = self._cache.get(key)
        if value is None:
            return None
        if self.decode_responses:
            return value
        return pickle.dumps(value)  # Return pickled data as the real Redis would

    async def set(self, key, value, ex=None):
        if not self.decode_responses:
            try:
                # If the value is already pickled, unpickle it first
                value = pickle.loads(value)
            except (pickle.UnpicklingError, TypeError):
                # If it's not pickled data, use as is
                pass
        self._cache[key] = value
        return True

    async def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        return count

    async def keys(self, pattern):
        # Simple pattern matching for testing
        import fnmatch
        return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

    async def incr(self, key):
        value = int(self._cache.get(key, 0)) + 1
        self._cache[key] = str(value)
        return value

    async def expire(self, key, time):
        return True


class MockRedisCache:
    """Mock Redis cache service for testing."""
    def __init__(self):
        self.redis_client = MockRedis(decode_responses=False)

    async def get(self, key):
        data = await self.redis_client.get(key)
        if data is not None:
            try:
                return pickle.loads(data)
            except (pickle.UnpicklingError, TypeError):
                return data
        return None

    async def set(self, key, value, expire=None):
        await self.redis_client.set(key, value, ex=expire)

    async def delete(self, key):
        await self.redis_client.delete(key)

    async def clear_pattern(self, pattern):
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)

    async def clear_user_cache(self, user_id):
        await self.clear_pattern(f"user:{user_id}:*")


def no_cache_response(expire: int = None):
    """Decorator that replaces Redis cache with pass-through for testing."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


mock_redis_cache = MockRedisCache()


@pytest.fixture(autouse=True)
def disable_redis_cache():
    """Disable Redis caching for tests."""
    with patch("redis.asyncio.Redis", return_value=MockRedis()):
        with patch("src.services.redis_cache.redis_cache", mock_redis_cache):
            with patch("src.services.redis_cache.cache_response", no_cache_response):
                with patch("src.api.contacts.cache_response", no_cache_response):
                    with patch("src.api.users.cache_response", no_cache_response):
                        with patch("src.api.contacts.redis_cache", mock_redis_cache):
                            with patch("src.api.users.redis_cache", mock_redis_cache):
                                yield


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="https://twitter.com/gravatar",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token
