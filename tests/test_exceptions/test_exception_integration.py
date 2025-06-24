from fastapi import FastAPI, status
from fastapi.testclient import TestClient
import pytest
from src.exceptions import register_exceptions, InvalidAccessToken, FrostyNotFound

@pytest.fixture(autouse=True)
def client():
    app = FastAPI()
    register_exceptions(app)

    @app.get("/invalid-token")
    def invalid_token_route():
        raise InvalidAccessToken()  

    @app.get("/frosty/{frost_id}")
    def frosty_route(frost_id: int):
        # detail override and frost_id attribute
        raise FrostyNotFound(frost_id=frost_id)


    return TestClient(app)  


# Integration Tests

def test_invalid_token_route(client):
    r = client.get("/invalid-token")
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json() == {"message": "Invalid or expired token provided."}


def test_frosty_not_found_route(client):
    r = client.get("/frosty/7")
    assert r.status_code == status.HTTP_404_NOT_FOUND
    # detail includes frost_id
    assert r.json() == {"message": "Frost item with id 7 not found or unauthorized user.", "frost_id": 7}

