import asyncio
import logging
import smtplib
import uuid
from email.mime.text import MIMEText
from typing import Any

from app.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)

_TEMPLATES: dict[str, tuple[str, str]] = {
    "like": (
        "Новый лайк",
        "{actor} поставил лайк вашему рецепту.",
    ),
    "comment": (
        "Новый комментарий",
        "{actor} оставил комментарий к вашему рецепту.",
    ),
    "reply": (
        "Ответ на комментарий",
        "{actor} ответил на ваш комментарий.",
    ),
    "follow": (
        "Новый подписчик",
        "{actor} подписался на вас.",
    ),
    "moderation": (
        "Сообщение от модератора",
        "{body}",
    ),
}


def _build_message(
    notification_type: str, actor: str | None, body: str | None
) -> tuple[str, str]:
    subject_tpl, text_tpl = _TEMPLATES.get(notification_type, ("Уведомление", "{body}"))
    text = text_tpl.format(actor=actor or "Система", body=body or "")
    return subject_tpl, text


def _send_smtp(
    host: str,
    port: int,
    tls: bool,
    user: str,
    password: str,
    from_addr: str,
    to_addr: str,
    message: str,
) -> None:
    if tls:
        with smtplib.SMTP_SSL(host, port) as smtp:
            if user:
                smtp.login(user, password)
            smtp.sendmail(from_addr, [to_addr], message)
    else:
        with smtplib.SMTP(host, port) as smtp2:
            if user:
                smtp2.login(user, password)
            smtp2.sendmail(from_addr, [to_addr], message)


async def _deliver_notification_email(
    notification_id: uuid.UUID,
    notification_repo: Any,
    user_repo: Any,
    preferences_repo: Any,
) -> bool:
    notification = await notification_repo.get_for_email_delivery(notification_id)
    if not notification or notification.email_sent_at is not None:
        return False

    recipient = await user_repo.get_by_id(notification.user_id)
    if not recipient:
        return False
    preferences = await preferences_repo.get_or_default(notification.user_id)
    notification_type = str(notification.type)
    if notification_type == "like" and not preferences.email_like:
        return False
    if notification_type in ("comment", "reply") and not preferences.email_comment:
        return False
    if notification_type == "follow" and not preferences.email_follow:
        return False

    actor_name = notification.actor.username if notification.actor else None
    subject, text = _build_message(notification_type, actor_name, notification.body)
    message = MIMEText(text, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = recipient.email

    _send_smtp(
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_tls,
        settings.smtp_user,
        settings.smtp_password,
        settings.smtp_from,
        recipient.email,
        message.as_string(),
    )
    # ponytail: SMTP has no idempotency key; use an outbox/provider key if
    # duplicates after a worker crash between send and commit become material.
    await notification_repo.mark_email_sent(notification)
    await notification_repo.session.commit()
    return True


@celery_app.task(  # type: ignore[misc]
    name="tasks.send_notification_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def send_notification_email(self: object, notification_id: str) -> None:
    import app.models  # noqa: F401
    from app.db.session import async_session_factory
    from app.repositories.notification import NotificationRepository
    from app.repositories.user import UserRepository

    if not settings.email_notifications_enabled:
        return

    async def _run() -> None:
        async with async_session_factory() as session:
            from app.repositories.notification_preferences import (
                NotificationPreferencesRepository,
            )

            await _deliver_notification_email(
                uuid.UUID(notification_id),
                NotificationRepository(session),
                UserRepository(session),
                NotificationPreferencesRepository(session),
            )

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error(
            "Failed to send email for notification %s: %s",
            notification_id,
            exc,
        )
        raise
