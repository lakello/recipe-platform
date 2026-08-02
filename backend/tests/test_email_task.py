import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.notification import NotificationType
from app.tasks.email import _deliver_notification_email


@pytest.mark.anyio
async def test_notification_email_is_sent_once() -> None:
    notification = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        type=NotificationType.like,
        actor=SimpleNamespace(username="chef"),
        body=None,
        email_sent_at=None,
    )
    notification_repo = AsyncMock()
    notification_repo.get_for_email_delivery.return_value = notification
    notification_repo.mark_email_sent.side_effect = lambda item: setattr(
        item, "email_sent_at", object()
    )
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = SimpleNamespace(email="user@example.com")
    preferences_repo = AsyncMock()
    preferences_repo.get_or_default.return_value = SimpleNamespace(
        email_like=True,
        email_comment=True,
        email_follow=True,
    )

    with patch("app.tasks.email._send_smtp") as send:
        assert await _deliver_notification_email(
            notification.id, notification_repo, user_repo, preferences_repo
        )
        assert not await _deliver_notification_email(
            notification.id, notification_repo, user_repo, preferences_repo
        )

    send.assert_called_once()
    notification_repo.mark_email_sent.assert_awaited_once_with(notification)
    notification_repo.session.commit.assert_awaited_once()
