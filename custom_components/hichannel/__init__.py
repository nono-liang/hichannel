"""HiChannel custom media source integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

DOMAIN = "hichannel"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True
