import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.follow import FollowService


def make_service(*, follow=None, user=None):
    follow_repo = AsyncMock()
    user_repo = AsyncMock()
    if follow is not None:
        follow_repo.get.return_value = follow
    if user is not None:
        user_repo.get_by_id.return_value = user
    return FollowService(follow_repo, user_repo), follow_repo, user_repo


@pytest.mark.asyncio
async def test_follow_success():
    user = MagicMock()
    service, follow_repo, _ = make_service(follow=None, user=user)
    follower_id = uuid.uuid4()
    following_id = uuid.uuid4()

    await service.follow(follower_id, following_id)

    follow_repo.create.assert_awaited_once_with(follower_id, following_id)


@pytest.mark.asyncio
async def test_follow_self_raises():
    service, _, _ = make_service(follow=None, user=MagicMock())
    uid = uuid.uuid4()
    with pytest.raises(Exception) as exc:
        await service.follow(uid, uid)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_follow_user_not_found():
    service, _, user_repo = make_service(follow=None, user=None)
    user_repo.get_by_id.return_value = None
    with pytest.raises(Exception) as exc:
        await service.follow(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_follow_already_following():
    existing = MagicMock()
    service, _, _ = make_service(follow=existing, user=MagicMock())
    with pytest.raises(Exception) as exc:
        await service.follow(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_unfollow_success():
    follow = MagicMock()
    service, follow_repo, _ = make_service(follow=follow)
    await service.unfollow(uuid.uuid4(), uuid.uuid4())
    follow_repo.delete.assert_awaited_once_with(follow)


@pytest.mark.asyncio
async def test_unfollow_not_following():
    service, _, _ = make_service(follow=None)
    with pytest.raises(Exception) as exc:
        await service.unfollow(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_followers_returns_page():
    service, follow_repo, _ = make_service()
    u = MagicMock()
    u.id = uuid.uuid4()
    u.username = "alice"
    u.avatar_url = None
    follow_repo.list_followers.return_value = ([u], 1)
    follow_repo.is_following_batch.return_value = set()

    page = await service.list_followers(uuid.uuid4(), uuid.uuid4(), 1, 20)

    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].username == "alice"


@pytest.mark.asyncio
async def test_list_following_returns_page():
    service, follow_repo, _ = make_service()
    u = MagicMock()
    u.id = uuid.uuid4()
    u.username = "bob"
    u.avatar_url = None
    follow_repo.list_following.return_value = ([u], 1)
    follow_repo.is_following_batch.return_value = {u.id}

    page = await service.list_following(uuid.uuid4(), uuid.uuid4(), 1, 20)

    assert page.total == 1
    assert page.items[0].is_following is True
