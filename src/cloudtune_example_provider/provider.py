from __future__ import annotations

import asyncio

from typing import Any
from urllib.parse import (
    parse_qs,
    urlparse,
)

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from media_provider_sdk import (
    MediaProvider,
    ProviderCapabilities,
    ProviderInvalidResponseError,
    ProviderItemNotFoundError,
    ProviderSearchError,
    ProviderSearchResult,
    ProviderStream,
    ProviderStreamError,
    ProviderTimeoutError,
)


class YTProvider(MediaProvider):
    provider_type = "YT"
    display_name = "YL Custom"

    @property
    def capabilities(
        self,
    ) -> ProviderCapabilities:
        return ProviderCapabilities(
            search=True,
            stream=True,
            preview=True,
            lyrics=False,
        )

    async def search(
        self,
        query: str,
        *,
        limit: int = 20,
    ) -> list[ProviderSearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            return []

        normalized_limit = max(
            1,
            min(
                limit,
                30,
            ),
        )

        try:
            info = await asyncio.to_thread(
                self._search_sync,
                normalized_query,
                normalized_limit,
            )

        except DownloadError as exception:
            raise ProviderSearchError(
                "YouTube search failed"
            ) from exception

        except TimeoutError as exception:
            raise ProviderTimeoutError(
                "YouTube search timed out"
            ) from exception

        if not info:
            return []

        entries = info.get(
            "entries"
        )

        if not isinstance(
            entries,
            list,
        ):
            raise ProviderInvalidResponseError(
                "YouTube search returned "
                "invalid entries"
            )

        results: list[
            ProviderSearchResult
        ] = []

        for entry in entries:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            video_id = entry.get(
                "id"
            )

            title = entry.get(
                "title"
            )

            if (
                not isinstance(
                    video_id,
                    str,
                )
                or not video_id
            ):
                continue

            if (
                not isinstance(
                    title,
                    str,
                )
                or not title
            ):
                continue

            artist = (
                self._optional_string(
                    entry.get(
                        "uploader"
                    )
                    or entry.get(
                        "channel"
                    )
                )
            )

            duration_seconds = (
                self._optional_int(
                    entry.get(
                        "duration"
                    )
                )
            )

            thumbnail_url = (
                self._get_thumbnail(
                    entry
                )
            )

            webpage_url = (
                "https://www.youtube.com/"
                f"watch?v={video_id}"
            )

            results.append(
                ProviderSearchResult(
                    provider_item_id=(
                        video_id
                    ),
                    title=title,
                    artist=artist,
                    album=None,
                    thumbnail_url=(
                        thumbnail_url
                    ),
                    duration_seconds=(
                        duration_seconds
                    ),
                    extra={
                        "webpage_url": (
                            webpage_url
                        ),
                        "channel_id": (
                            entry.get(
                                "channel_id"
                            )
                        ),
                        "uploader_id": (
                            entry.get(
                                "uploader_id"
                            )
                        ),
                    },
                )
            )

        return results[
            :normalized_limit
        ]

    def _search_sync(
        self,
        query: str,
        limit: int,
    ) -> dict[str, Any] | None:
        options: dict[
            str,
            Any,
        ] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "ignoreerrors": True,
            "ignoreconfig": True,
            "playlistend": limit,
        }

        search_url = (
            f"ytsearch{limit}:{query}"
        )

        with YoutubeDL(
            options
        ) as ydl:
            extracted = (
                ydl.extract_info(
                    search_url,
                    download=False,
                )
            )

        if extracted is None:
            return None

        if not isinstance(
            extracted,
            dict,
        ):
            raise ProviderInvalidResponseError(
                "YouTube search returned "
                "an invalid response"
            )

        return extracted

    async def get_stream(
        self,
        provider_item_id: str,
    ) -> ProviderStream:
        return await asyncio.to_thread(
            self._get_stream_sync,
            provider_item_id,
        )

    def _get_stream_sync(
        self,
        provider_item_id: str,
    ) -> ProviderStream:
        video_id = (
            provider_item_id
            .strip()
        )

        if not video_id:
            raise ProviderItemNotFoundError(
                "YouTube video ID is missing"
            )

        youtube_url = (
            "https://www.youtube.com/"
            f"watch?v={video_id}"
        )

        options: dict[
            str,
            Any,
        ] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "ignoreconfig": True,

            # Prefer audio that works well with
            # iOS / Android / Flutter.
            "format": (
                "bestaudio[ext=m4a]"
                "/bestaudio"
            ),
        }

        try:
            with YoutubeDL(
                options
            ) as ydl:
                info = (
                    ydl.extract_info(
                        youtube_url,
                        download=False,
                    )
                )

        except DownloadError as exception:
            raise ProviderStreamError(
                "Unable to resolve "
                "YouTube stream"
            ) from exception

        except TimeoutError as exception:
            raise ProviderTimeoutError(
                "YouTube stream request "
                "timed out"
            ) from exception

        if not isinstance(
            info,
            dict,
        ):
            raise ProviderInvalidResponseError(
                "YouTube returned invalid "
                "media information"
            )

        stream_url = info.get(
            "url"
        )

        if (
            not isinstance(
                stream_url,
                str,
            )
            or not stream_url
        ):
            raise ProviderStreamError(
                "yt-dlp returned no "
                "playable stream URL"
            )

        headers = (
            self._extract_headers(
                info
            )
        )

        duration_seconds = (
            self._optional_int(
                info.get(
                    "duration"
                )
            )
        )

        content_length = (
            self._resolve_content_length(
                info
            )
        )

        container = (
            self._optional_string(
                info.get(
                    "container"
                )
            )
            or self._optional_string(
                info.get(
                    "ext"
                )
            )
        )

        codec = (
            self._optional_string(
                info.get(
                    "acodec"
                )
            )
        )

        format_id = (
            self._optional_string(
                info.get(
                    "format_id"
                )
            )
        )

        return ProviderStream(
            url=stream_url,
            mime_type=(
                self._resolve_mime_type(
                    info
                )
            ),
            expires_at_epoch=(
                self._extract_expiry_epoch(
                    stream_url
                )
            ),
            headers=headers,

            # Provider returns the native source.
            # Server PlaybackPolicy decides whether
            # it remains DIRECT or is repackaged to HLS.
            stream_type="DIRECT",

            duration_seconds=(
                duration_seconds
            ),
            content_length=(
                content_length
            ),
            container=container,
            codec=codec,
            format_id=format_id,

            extra={
                "webpage_url": (
                    youtube_url
                ),
            },
        )

    @staticmethod
    def _extract_headers(
        info: dict[str, Any],
    ) -> dict[str, str]:
        raw_headers = info.get(
            "http_headers"
        )

        if not isinstance(
            raw_headers,
            dict,
        ):
            return {}

        return {
            str(key): str(value)
            for key, value
            in raw_headers.items()
            if value is not None
        }

    @staticmethod
    def _resolve_content_length(
        info: dict[str, Any],
    ) -> int | None:
        for key in (
            "filesize",
            "filesize_approx",
        ):
            value = info.get(
                key
            )

            if (
                isinstance(
                    value,
                    int,
                )
                and not isinstance(
                    value,
                    bool,
                )
                and value >= 0
            ):
                return value

        return None

    @staticmethod
    def _get_thumbnail(
        entry: dict[str, Any],
    ) -> str | None:
        thumbnail = entry.get(
            "thumbnail"
        )

        if (
            isinstance(
                thumbnail,
                str,
            )
            and thumbnail
        ):
            return thumbnail

        thumbnails = entry.get(
            "thumbnails"
        )

        if not isinstance(
            thumbnails,
            list,
        ):
            return None

        for item in reversed(
            thumbnails
        ):
            if not isinstance(
                item,
                dict,
            ):
                continue

            url = item.get(
                "url"
            )

            if (
                isinstance(
                    url,
                    str,
                )
                and url
            ):
                return url

        return None

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if (
            isinstance(
                value,
                str,
            )
            and value.strip()
        ):
            return value.strip()

        return None

    @staticmethod
    def _optional_int(
        value: Any,
    ) -> int | None:
        if isinstance(
            value,
            bool,
        ):
            return None

        if isinstance(
            value,
            int,
        ):
            return value

        if isinstance(
            value,
            float,
        ):
            return int(
                value
            )

        return None

    @staticmethod
    def _extract_expiry_epoch(
        stream_url: str,
    ) -> int | None:
        query = parse_qs(
            urlparse(
                stream_url
            ).query
        )

        values = query.get(
            "expire"
        )

        if not values:
            return None

        try:
            return int(
                values[0]
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _resolve_mime_type(
        info: dict[str, Any],
    ) -> str | None:
        ext = info.get(
            "ext"
        )

        audio_codec = info.get(
            "acodec"
        )

        if isinstance(
            ext,
            str,
        ):
            ext = ext.lower()

        else:
            ext = None

        mime_types = {
            "m4a": "audio/mp4",
            "mp4": "audio/mp4",
            "webm": "audio/webm",
            "mp3": "audio/mpeg",
            "aac": "audio/aac",
            "ogg": "audio/ogg",
            "opus": "audio/ogg",
            "wav": "audio/wav",
            "flac": "audio/flac",
        }

        if ext in mime_types:
            return mime_types[
                ext
            ]

        if audio_codec == "opus":
            return "audio/webm"

        if (
            isinstance(
                audio_codec,
                str,
            )
            and audio_codec.startswith(
                "mp4a"
            )
        ):
            return "audio/mp4"

        return None