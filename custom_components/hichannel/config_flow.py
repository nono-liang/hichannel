"""Config flow for HiChannel — single-step, no user input required."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN


class HiChannelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HiChannel."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        # Only one entry is meaningful; abort if already configured.
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="HiChannel", data={})
