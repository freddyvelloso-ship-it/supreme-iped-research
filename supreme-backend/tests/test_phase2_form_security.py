import pytest

from src.app.api.psychometric import FormLinkRequest, create_form_link


@pytest.mark.asyncio
async def test_phase2_form_link_does_not_put_ticket_in_url():
    response = await create_form_link(FormLinkRequest(id_hash="participant-a", instrument="PANAS_SHORT"))

    assert response["url"] == "/forms/panas/start"
    assert response["launch_url"].startswith("/forms/panas/launch/")
    assert "access_code" in response
    assert "ticket=" not in response["url"]
    assert "token=" not in response["url"]
    assert "?ticket=" not in response["launch_url"]
    assert "?token=" not in response["launch_url"]
