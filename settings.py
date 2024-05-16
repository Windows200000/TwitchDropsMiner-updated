from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from constants import DEFAULT_LANG, SETTINGS_PATH
from utils import json_load, json_save
from yarl import URL

if TYPE_CHECKING:
    from main import ParsedArgs


class SettingsFile(TypedDict):
    proxy: URL
    language: str
    autostart: bool
    exclude: set[str]
    priority: list[str]
    priority_only: bool
    autostart_tray: bool
    connection_quality: int
    tray_notifications: bool


default_settings: SettingsFile = {
    "proxy": URL(),
    "priority": [],
    "exclude": set(),
    "autostart": False,
    "priority_only": True,
    "autostart_tray": False,
    "connection_quality": 1,
    "language": DEFAULT_LANG,
    "tray_notifications": True,
}


class Settings:
    # from args
    log: bool
    tray: bool
    no_run_check: bool
    # args properties
    debug_ws: int
    debug_gql: int
    logging_level: int
    # from settings file
    proxy: URL
    language: str
    autostart: bool
    exclude: set[str]
    priority: list[str]
    priority_only: bool
    autostart_tray: bool
    connection_quality: int
    tray_notifications: bool

    PASSTHROUGH = ("_settings", "_args", "_altered")

    def __init__(self, args: ParsedArgs) -> None:
        self._settings: SettingsFile = json_load(SETTINGS_PATH, default_settings)
        self._args: ParsedArgs = args
        self._altered: bool = False

    # default logic of reading settings is to check args first, then the settings file
    def __getattr__(self, name: str, /) -> Any:
        if name in self.PASSTHROUGH:
            # passthrough
            return getattr(super(), name)
        if hasattr(self._args, name):
            return getattr(self._args, name)
        if name in self._settings:
            return self._settings[name]  # type: ignore[literal-required]
        return getattr(super(), name)

    def __setattr__(self, name: str, value: Any, /) -> None:
        if name in self.PASSTHROUGH:
            # passthrough
            return super().__setattr__(name, value)
        if name in self._settings:
            self._settings[name] = value  # type: ignore[literal-required]
            self._altered = True
            return None
        msg = f"{name} is missing a custom setter"
        raise TypeError(msg)

    def __delattr__(self, name: str, /) -> None:
        msg = "settings can't be deleted"
        raise RuntimeError(msg)

    def alter(self) -> None:
        self._altered = True

    def save(self, *, force: bool = False) -> None:
        if self._altered or force:
            json_save(SETTINGS_PATH, self._settings, sort=True)
