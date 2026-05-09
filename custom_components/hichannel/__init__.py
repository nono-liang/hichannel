"""HiChannel custom media source integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "hichannel"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    from .media_source import HiChannelMediaSource

    # Register our provider into hass.data["media_source"] so that
    # media-source://hichannel/... URIs are resolvable.
    ms_sources = hass.data.get("media_source")
    if isinstance(ms_sources, dict):
        ms_sources[DOMAIN] = HiChannelMediaSource(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ms_sources = hass.data.get("media_source")
    if isinstance(ms_sources, dict):
        ms_sources.pop(DOMAIN, None)
    return True
