import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_app_without_dependencies():
    """Test app without overriding any dependencies"""
    from src.__init__ import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # This should work even if the endpoint doesn't exist
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404