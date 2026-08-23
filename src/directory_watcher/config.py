import yaml

def load_config(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")

    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}")

    return config

SETTINGS = load_config("config.yaml")
WATCH_PATH = SETTINGS["app"]["watch_path"]
