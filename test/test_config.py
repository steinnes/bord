import json
import tempfile
import pytest
from contextlib import contextmanager

from bord.config import Config, init_config


@pytest.fixture
def config_file():
    @contextmanager
    def inner(**overrides):
        config = {"interval": 10, "urls": ["https://a.com", "https://b.com"]}
        config = {**config, **overrides}
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(json.dumps(config).encode("utf-8"))
            fp.seek(0)
            yield fp.name

    return inner


def test_config_defaults(config_file):
    # Arrange
    with config_file() as f:
        # Act
        cfg = init_config(f)

        # Assert
        assert len(cfg.urls) == 2
        assert cfg.interval == 10
        assert cfg.executable_path is None


def test_config_overrides(config_file):
    # Arrange
    with config_file(interval=1, urls=["https://c.com"], executable_path="/usr/bin/chromium") as f:
        # Act
        cfg = init_config(f)

        # Assert
        assert len(cfg.urls) == 1
        assert cfg.interval == 1
        assert cfg.executable_path == "/usr/bin/chromium"
