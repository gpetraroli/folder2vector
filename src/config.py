import os
from pathlib import Path

import yaml


def config_path() -> Path:
    if explicit := os.environ.get("FOLDER2VECTOR_CONFIG"):
        return Path(explicit)
    return Path.cwd() / "config.yaml"


def load_config(path: str | Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")

    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}")

    return config


SETTINGS = load_config(config_path())
WATCH_PATH = SETTINGS["app"]["watch_path"]
