import pytest

@pytest.mark.asyncio
async def test_get_contacts_without_token(client):
    response = await client.get("/api/contacts/", follow_redirects=True)
    assert response.status_code == 401