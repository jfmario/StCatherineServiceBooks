from __future__ import annotations

from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from liturgics.models import Component, Config, ResolvedComponent
from liturgics.sources.base import cache_key, slice_pdf


def _download_from_s3(bucket: str, key: str, destination: Path, region: str | None) -> None:
    session_kwargs: dict = {}
    if region:
        session_kwargs["region_name"] = region

    client = boto3.client("s3", **session_kwargs)
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        client.download_file(bucket, key, str(destination))
    except ClientError as exc:
        raise FileNotFoundError(
            f"Library PDF not found in s3://{bucket}/{key}"
        ) from exc


def resolve_library_pdf(component: Component, config: Config) -> ResolvedComponent:
    if not config.library_bucket:
        raise EnvironmentError(
            "LITURGICS_LIBRARY_BUCKET must be set when using library-pdf components"
        )

    download_path = config.cache_dir / "library" / "downloads" / component.path
    if not download_path.is_file():
        _download_from_s3(
            config.library_bucket,
            component.path,
            download_path,
            config.aws_region,
        )

    range_suffix = ""
    if component.pages:
        start = component.pages.start or 1
        end = component.pages.end or "end"
        range_suffix = f"_{start}_{end}"

    cache_path = (
        config.cache_dir
        / "library"
        / "slices"
        / f"{cache_key(component.key, component.path, range_suffix)}.pdf"
    )
    page_count = slice_pdf(download_path, component.pages, cache_path)

    return ResolvedComponent(
        component=component,
        pdf_path=cache_path,
        page_count=page_count,
    )
