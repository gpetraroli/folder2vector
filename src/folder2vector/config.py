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


def get_source_path_to_store(absolute_file_path: str) -> str:
    path = Path(absolute_file_path).resolve()
    if not STORE_RELATIVE_PATH:
        return str(path)
    
    watch = Path(WATCH_PATH).resolve()
    
    return path.relative_to(watch).as_posix()


SETTINGS = load_config(config_path())
WATCH_PATH = SETTINGS["app"]["watch_path"]
OLLAMA_URL = SETTINGS["app"]["ollama_url"]
EMBEDDING_MODEL = SETTINGS["app"]["embedding_model"]
DB_CONNECTION = SETTINGS["app"]["db_connection"]
COLLECTION_NAME = SETTINGS["app"]["collection_name"]
CHUNK_SIZE = SETTINGS["app"]["chunk_size"]
CHUNK_OVERLAP = SETTINGS["app"]["chunk_overlap"]
OCR_MODEL = SETTINGS["app"]["ocr_model"]
SETTLE_SECONDS = SETTINGS["app"]["settle_seconds"]
STORE_RELATIVE_PATH = SETTINGS["app"]["store_relative_path"]