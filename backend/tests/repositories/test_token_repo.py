import pytest
from datetime import datetime, timedelta

from app.models.user.token_blacklist import TokenBlackList


@pytest.mark.asyncio
async def test_add_to_blacklist(token_repo):
    expires_at = datetime.now() + timedelta(minutes=30)

    token = TokenBlackList(
        token="test_token_123",
        expires_at=expires_at
    )

    new_token = await token_repo.add_to_blacklist(token)

    assert new_token.id is not None
    assert new_token.token == "test_token_123"
    assert new_token.expires_at == expires_at


@pytest.mark.asyncio
async def test_is_token_blacklisted_true(token_repo):
    token = TokenBlackList(
        token="blacklisted_token_123",
        expires_at=datetime.now() + timedelta(minutes=30)
    )

    await token_repo.add_to_blacklist(token)

    result = await token_repo.is_token_blacklisted(
        "blacklisted_token_123"
    )

    assert result is True


@pytest.mark.asyncio
async def test_is_token_blacklisted_false(token_repo):
    result = await token_repo.is_token_blacklisted(
        "not_blacklisted_token_123"
    )

    assert result is False
