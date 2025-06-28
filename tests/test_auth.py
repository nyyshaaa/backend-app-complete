import pytest,asyncio
from unittest.mock import AsyncMock,Mock
from httpx import AsyncClient
from src.auth.dependencies import AccessTokenBearer
from src.auth.services import UserService
from src.__init__ import app 
from src.db.dependencies import get_session
from src.auth.schemas import UserCreateInput

mock_session=AsyncMock()

async def override_get_session():
    yield mock_session

app.dependency_overrides[get_session]=override_get_session

mock_user_service=Mock(spec=UserService)

@pytest.fixture()
def fake_session():
    return mock_session

@pytest.fixture()
def fake_user_service():
    return mock_user_service



async def override_access_token_bearer()->dict:
    return {"user":{'email':'nyshaaa@dreamer.com','user_id':1}}

app.dependency_overrides[AccessTokenBearer]=override_access_token_bearer

signup_data={
    "username": "nysha",
    "email": "nysha@dreamer.com",
    "password": "password"
}

fake_user={
    "id":1,
    "name":"name",
    "about":"about",
    "email":"email"
}


@pytest.fixture
async def client():
    async with AsyncClient(app=app,base_url="http://testserver") as ac:
        yield ac


async def test_signup_access(fake_session,fake_user_service,client):
    fake_user_service.get_user_id_email=AsyncMock(return_value=None)
    fake_user_service.create_user=AsyncMock(return_value=fake_user)

    fake_user_service.get_user_id_email.assert_awaited_once_with(signup_data["email"],fake_session)
    fake_user_service.create_user.assert_called_once_with(UserCreateInput(**signup_data),fake_session)

    response=await client.post("/api/v1/auth/signup",json=signup_data)
    assert response.status_code==200

    