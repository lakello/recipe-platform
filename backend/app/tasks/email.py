import asyncio
import logging
import smtplib
import uuid
from email.mime.text import MIMEText

from app.celery_app import celery_app

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
    from app.core.config import settings
    from app.db.session import async_session_factory
    from app.repositories.notification import NotificationRepository
    from app.repositories.user import UserRepository

    if not settings.email_notifications_enabled:
        return

    async def _fetch() -> tuple[str, str, str | None, str | None] | None:
        async with async_session_factory() as session:
            n_repo = NotificationRepository(session)
            u_repo = UserRepository(session)
            n = await n_repo.get_by_id(uuid.UUID(notification_id))
            if not n:
                return None
            recipient = await u_repo.get_by_id(n.user_id)
            if not recipient:
                return None
            actor_name = n.actor.username if n.actor else None
            return recipient.email, str(n.type), actor_name, n.body

    result = asyncio.run(_fetch())
    if not result:
        logger.warning("Notification %s not found, skipping email", notification_id)
        return

    to_email, notif_type, actor_name, body = result
    subject, text = _build_message(notif_type, actor_name, body)

    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    try:
        _send_smtp(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_tls,
            settings.smtp_user,
            settings.smtp_password,
            settings.smtp_from,
            to_email,
            msg.as_string(),
        )
    except Exception as exc:
        logger.error(
            "Failed to send email for notification %s to %s: %s",
            notification_id,
            to_email,
            exc,
        )
        raise
