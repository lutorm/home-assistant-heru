"""Button platform for HERU."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now as hass_now
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BUTTON_CLASS_SET_TIME,
    BUTTON_CLASS_START,
    DOMAIN,
    HERU_BUTTONS,
)

from .entity import HeruEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup button platform."""
    _LOGGER.debug("Heru.button.py")
    coordinator = hass.data[DOMAIN]["coordinator"]

    buttons = []
    for button in HERU_BUTTONS:
        if button["entity_class"] == BUTTON_CLASS_START:
            buttons.append(HeruButtonStart(coordinator, button, entry))
        elif button["entity_class"] == BUTTON_CLASS_SET_TIME:
            buttons.append(HeruButtonSetTime(coordinator, button, entry))
    async_add_devices(buttons)


class HeruButton(HeruEntity, ButtonEntity):
    """HERU button class."""

    def __init__(self, coordinator: CoordinatorEntity, idx, entry):
        _LOGGER.debug("HeruButton.__init__()")
        super().__init__(coordinator, idx, entry)
        self.coordinator = coordinator
        self.idx = idx
        self.modbus_address = self.idx["modbus_address"]


class HeruButtonStart(HeruButton):
    """HERU start button class."""

    async def async_press(self) -> None:
        """Press the button."""
        _LOGGER.debug("HeruButtonStart.async_press()")
        result = await self.coordinator.write_coil_by_address(self.modbus_address, True)
        _LOGGER.debug("async_press: %s", result)


class HeruButtonSetTime(HeruButton):
    """HERU start button class."""

    async def async_press(self) -> None:
        """Press the button."""
        _LOGGER.debug("HeruButtonSetTime.async_press()")

        now = hass_now()
        await self.coordinator.write_register_by_address("4x00400", now.year)
        await self.coordinator.write_register_by_address("4x00401", now.month)
        await self.coordinator.write_register_by_address("4x00402", now.day)
        await self.coordinator.write_register_by_address("4x00403", now.hour)
        await self.coordinator.write_register_by_address("4x00404", now.minute)
        await self.coordinator.write_register_by_address("4x00405", now.second)
