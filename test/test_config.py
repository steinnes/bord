import json
import tempfile
import pytest
from contextlib import contextmanager

from bord.config import Config, init_config


@pytest.fixture
def config_file():
    configs = {
        1: {"interval": 10, "urls": ["https://a.com", "https://b.com"]},
        2: {
            "version": 2,
            "screens": [
                {"url": "https://a.com", "display_time": 10},
                {"url": "https://b.com", "display_time": 10},
            ],
        },
    }

    @contextmanager
    def inner(version=2, **overrides):
        config = {**configs[version], **overrides}
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(json.dumps(config).encode("utf-8"))
            fp.seek(0)
            yield fp.name

    return inner


@pytest.mark.parametrize("config_version", [1, 2], ids=["config_v1", "config_v2"])
def test_config_defaults(config_file, config_version):
    # Arrange
    with config_file(version=config_version) as f:
        # Act
        cfg = init_config(f)

        # Assert
        assert len(cfg.screens) == 2
        assert [screen.display_time for screen in cfg.screens] == [10, 10]
        assert cfg.executable_path is None


def test_config_v1_overrides(config_file):
    # Arrange
    with config_file(version=1, interval=1, urls=["https://c.com"], executable_path="/usr/bin/chromium") as f:
        # Act
        cfg = init_config(f)

        # Assert
        assert len(cfg.screens) == 1
        assert [screen.display_time for screen in cfg.screens] == [1]
        assert cfg.executable_path == "/usr/bin/chromium"


def test_config_v2_overrides(config_file):
    # Arrange
    with config_file(
        version=2,
        screens=[
            {"url": "https://c.com", "refresh_interval": 60, "display_time": 10},
            {"url": "https://b.com", "display_time": 60},
        ],
        executable_path="/usr/bin/chromium",
    ) as f:
        # Act
        cfg = init_config(f)

        # Assert
        assert len(cfg.screens) == 2
        assert cfg.screens[0].refresh_interval == 60
        assert cfg.screens[0].display_time == 10
        assert cfg.screens[1].refresh_interval is None
        assert cfg.screens[1].display_time == 60
        assert cfg.executable_path == "/usr/bin/chromium"
