import os
import json
from typing import List, Optional
from dataclasses import dataclass
import logging

from screeninfo import get_monitors, Enumerator, Monitor

logger = logging.getLogger(__name__)


@dataclass
class Screen:
    url: str
    display_time: Optional[int] = 30
    refresh_interval: Optional[int] = None


@dataclass(frozen=True)
class Config:
    monitor: Monitor
    screens: List[Screen]
    version: int = 2
    executable_path: Optional[str] = None


class ConfigV2:
    def __init__(self, **kwargs):
        self.screens: List[Screen] = []
        screens = kwargs.pop("screens")
        for s in screens:
            self.screens.append(Screen(**s))
        self.kwargs = kwargs

    def to_config(self):
        return Config(screens=self.screens, **self.kwargs)


@dataclass(frozen=True)
class ConfigV1:
    interval: int
    urls: List[str]
    monitor: Monitor
    executable_path: Optional[str] = None

    def to_config(self):
        return Config(
            monitor=self.monitor,
            screens=[Screen(url=u, display_time=self.interval, refresh_interval=None) for u in self.urls],
            executable_path=self.executable_path,
        )


def _get_system_graphics_subsystem():
    system = os.uname()
    supported = {"Linux": Enumerator.Xinerama, "Darwin": Enumerator.OSX}
    try:
        return supported[system.sysname]
    except KeyError as e:
        raise Exception(f"Detecting monitors and resolution is not supported for {system.sysname}") from e


def init_config(config_path: str = None):
    cfgversions = {1: ConfigV1, 2: ConfigV2}
    if config_path is None:
        config_path = "./config.json"

    with open(config_path) as fp:
        cfg_json = json.load(fp)

    if cfg_json.get("version") is not None:
        try:
            cfg_class = cfgversions[cfg_json.get("version")]
        except KeyError:
            pass
    else:
        cfg_class = ConfigV1

    monitors = [monitor for monitor in get_monitors(_get_system_graphics_subsystem())]
    if len(monitors) > 1:
        logger.warning("Multiple monitors detected, using monitor[0]=", monitors[0])

    cfg = cfg_class(monitor=monitors[0], **cfg_json)
    return cfg.to_config()
