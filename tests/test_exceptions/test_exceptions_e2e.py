import asyncio
from fastapi import status
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from src.__init__ import app
from src.exceptions import FrostyNotFound, InvalidAccessToken, UserNotFound
from src.products.routes import get_frosty
from src.users.utils import  get_user_public_info
from src.config import configSettgs
from asgi_lifespan import LifespanManager


TEST_ACCESS_TOKEN=configSettgs.TEST_TOKEN



@pytest.fixture
async def client():
    async with LifespanManager(app):  
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            yield ac
    

# @pytest.mark.asyncio
# async def test_invalid_access_token_e2e(client):
#     # Simulate a dependency that always raises InvalidAccessToken
#     async def always_raise_invalid_token():
#         raise InvalidAccessToken()
#     # Patch a dependency (example: AccessTokenBearer) to raise the exception
#     from src.auth.dependencies import AccessTokenBearer
#     app.dependency_overrides[AccessTokenBearer] = always_raise_invalid_token

#     response = await client.get("/api/v1/auth/profile")
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     assert response.json()["message"] == "Invalid access token provided."

#     # Clean up
#     app.dependency_overrides.pop(AccessTokenBearer, None)


@pytest.mark.anyio
async def test_frosty_not_found(client):
    # Stub out DB lookup to always raise
    async def missing_frosty(frost_id: int):
        raise FrostyNotFound(frost_id=frost_id)
    app.dependency_overrides[get_frosty] = missing_frosty

    r = await client.get("/api/v1/frosties/1234324235",headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"})
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json() == {
        "message": "Frost item with id 1234324235 not found or unauthorized user.",
        "frost_id": 1234324235,
    }

    app.dependency_overrides.pop(get_frosty, None)

@pytest.mark.anyio
async def test_user_not_found(client):
    # Stub out DB lookup to always raise
    async def missing_user():
        raise UserNotFound()
    app.dependency_overrides[get_user_public_info] = missing_user

    r = await client.get("/api/v1/profile/42")
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json() == {"message": "User not found."}

    app.dependency_overrides.pop(get_user_public_info, None)