"""HiChannel media source platform."""
from __future__ import annotations

import re
import logging

from homeassistant.components.media_source.models import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

MIME_HLS = "application/x-mpegURL"
# Browse-time content type: must start with "audio/" so Google Cast (Nest
# Audio/Mini, speaker groups) doesn't hide the item via its audio_content_filter.
BROWSE_MIME_HLS = "audio/mpegurl"

CHANNELS: dict[str, dict] = {
    "bestradio": {
        "name": "Best Radio 好事聯播網",
        "url": "http://www.bestradio.com.tw",
        "thumbnail": None,
        "resolver": "page_regex",
    },
    "hitoradio": {
        "name": "Hit FM聯播網",
        "url": "https://www.hitoradio.com",
        "thumbnail": None,
        "resolver": "api_post",
        "api_url": "https://www.hitoradio.com/newweb/hichannel.php",
        "api_data": "channelID=1&action=getLIVEURL",
    },
}

# Ordered list of regex patterns to locate the m3u8 src on the target page.
# Each pattern captures the URL in group 1.
_M3U8_PATTERNS: list[re.Pattern] = [
    # <video id="video1" src="...m3u8...">  (src after id)
    re.compile(
        r'id=["\']video1["\'][^>]*\bsrc=["\']([^"\']+\.m3u8[^"\']*)["\']',
        re.IGNORECASE,
    ),
    # <video src="...m3u8..." id="video1">  (src before id)
    re.compile(
        r'\bsrc=["\']([^"\']+\.m3u8[^"\']*)["\'][^>]*id=["\']video1["\']',
        re.IGNORECASE,
    ),
    # <source src="...m3u8..."> inside a block that also contains id="video1"
    re.compile(
        r'id=["\']video1["\'].*?<source[^>]*\bsrc=["\']([^"\']+\.m3u8[^"\']*)["\']',
        re.IGNORECASE | re.DOTALL,
    ),
    # JavaScript assignment: var video1 = "...m3u8..." or similar
    re.compile(
        r'video1[^=]*=[^"\']*["\']([^"\']+\.m3u8[^"\']*)["\']',
        re.IGNORECASE,
    ),
]


async def async_get_media_source(hass: HomeAssistant) -> HiChannelMediaSource:
    """Return the HiChannel media source."""
    return HiChannelMediaSource(hass)


class HiChannelMediaSource(MediaSource):
    """Provides media-source://hichannel/{channel_id} URIs."""

    name = "HiChannel"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    # ------------------------------------------------------------------
    # Resolve: turn a channel identifier into a playable stream URL
    # ------------------------------------------------------------------

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        channel_id = item.identifier
        if channel_id not in CHANNELS:
            raise ValueError(f"HiChannel: unknown channel '{channel_id}'")

        channel = CHANNELS[channel_id]
        stream_url = await self._resolve_stream(channel_id, channel)
        _LOGGER.debug("HiChannel resolved %s -> %s", channel_id, stream_url)
        return PlayMedia(stream_url, MIME_HLS)

    # ------------------------------------------------------------------
    # Browse: list channels or show a single channel card
    # ------------------------------------------------------------------

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        if item.identifier:
            return self._channel_source(item.identifier)

        return BrowseMediaSource(
            domain=DOMAIN,
            identifier="",
            media_class="directory",
            media_content_type="",
            title="HiChannel",
            can_play=False,
            can_expand=True,
            children=[
                self._channel_source(cid) for cid in CHANNELS
            ],
            children_media_class="music",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _channel_source(self, channel_id: str) -> BrowseMediaSource:
        if channel_id not in CHANNELS:
            raise ValueError(f"HiChannel: unknown channel '{channel_id}'")
        ch = CHANNELS[channel_id]
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=channel_id,
            media_class="music",
            media_content_type=BROWSE_MIME_HLS,
            title=ch["name"],
            can_play=True,
            can_expand=False,
            thumbnail=ch.get("thumbnail"),
        )

    async def _resolve_stream(self, channel_id: str, channel: dict) -> str:
        """Resolve the m3u8 stream URL for a channel."""
        resolver = channel.get("resolver", "page_regex")
        session = async_get_clientsession(self.hass)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

        if resolver == "api_post":
            api_url = channel["api_url"]
            post_headers = {
                **headers,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": channel["url"],
            }
            async with session.post(
                api_url,
                data=channel["api_data"],
                headers=post_headers,
                timeout=10,
            ) as resp:
                resp.raise_for_status()
                body = (await resp.text()).strip()

            m = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', body)
            if m:
                return m.group(0)

            raise ValueError(
                f"HiChannel: could not find m3u8 stream for '{channel_id}' "
                f"in POST response from {api_url}"
            )

        page_url = channel["url"]
        async with session.get(page_url, headers=headers, timeout=10) as resp:
            resp.raise_for_status()
            html = await resp.text()

        for pattern in _M3U8_PATTERNS:
            m = pattern.search(html)
            if m:
                return m.group(1)

        raise ValueError(
            f"HiChannel: could not find m3u8 stream for '{channel_id}' at {page_url}"
        )
