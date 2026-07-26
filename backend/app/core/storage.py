from typing import Any

import boto3
from botocore.config import Config

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def get_s3_client() -> Any:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4"),
    )


def _get_presign_client() -> Any:
    # Presigned URLs must be signed with the public endpoint so that the
    # hostname in the signature matches the host the browser actually calls.
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_public_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4"),
    )


def presign_post(
    bucket: str,
    key: str,
    content_type: str,
    max_bytes: int,
    expires_in: int = 600,
) -> dict[str, Any]:
    return dict(
        _get_presign_client().generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, max_bytes],
            ],
            ExpiresIn=expires_in,
        )
    )


def presign_get(bucket: str, key: str, expires_in: int = 3600) -> str:
    return str(
        _get_presign_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    )


def head_object(bucket: str, key: str) -> dict[str, Any]:
    return dict(get_s3_client().head_object(Bucket=bucket, Key=key))


def get_object_bytes(bucket: str, key: str) -> bytes:
    return bytes(get_s3_client().get_object(Bucket=bucket, Key=key)["Body"].read())


def put_object(bucket: str, key: str, body: bytes, content_type: str) -> None:
    get_s3_client().put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


def delete_object(bucket: str, key: str) -> None:
    get_s3_client().delete_object(Bucket=bucket, Key=key)


def public_url(bucket: str, key: str) -> str:
    base = settings.s3_public_url.rstrip("/")
    return f"{base}/{bucket}/{key}"
