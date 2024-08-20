import json
import os
from pathlib import Path
from typing import Union, Any, get_type_hints, Optional

from dotenv import load_dotenv
from oterm.utils import get_default_data_dir

load_dotenv()

class EnvConfigError(Exception):
    """Custom exception for EnvConfig errors."""
    pass

def _parse_bool(val: Union[str, bool]) -> bool:
    """Parse a value to a boolean."""
    if isinstance(val, bool):
        return val
    return val.lower() in {"true", "yes", "1"}

class EnvConfig:
    """
    Map environment variables to class fields:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
    """

    ENV: str = "development"
    OLLAMA_HOST: str = "0.0.0.0:11434"
    OLLAMA_URL: str = ""
    OTERM_VERIFY_SSL: bool = True
    OTERM_DATA_DIR: Path = get_default_data_dir()

    def __init__(self, env: dict[str, str]):
        for field, var_type in get_type_hints(EnvConfig).items():
            if field.isupper():
                self._set_field(env, field, var_type)

        if not self.OLLAMA_URL:
            self.OLLAMA_URL = f"http://{self.OLLAMA_HOST}"

    def _set_field(self, env: dict[str, str], field: str, var_type: type):
        """Set a field in EnvConfig with type casting."""
        default_value = getattr(self, field, None)
        env_value = env.get(field, default_value)
        
        if env_value is None and default_value is None:
            raise EnvConfigError(f"The {field} field is required")
        
        try:
            if var_type is bool:
                value = _parse_bool(env_value)
            elif var_type == list[str]:
                value = json.loads(env_value) if env_value else default_value
            else:
                value = var_type(env_value)
            setattr(self, field, value)
        except (ValueError, TypeError) as e:
            raise EnvConfigError(
                f'Unable to cast value of "{env_value}" to type "{var_type}" for "{field}" field'
            ) from e

    def __repr__(self):
        return repr(self.__dict__)

# Expose EnvConfig object for app to import
envConfig = EnvConfig(os.environ)

class AppConfig:
    """Class to manage application configuration."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path or envConfig.OTERM_DATA_DIR / "config.json"
        self._data = {"theme": "dark"}
        self._load_config()

    def _load_config(self):
        """Load configuration from a file, or initialize if not present."""
        if self._path.exists():
            with self._path.open("r") as f:
                saved = json.load(f)
                self._data.update(saved)
        else:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self.save()

    def set(self, key: str, value: Any):
        """Set a configuration value and save it."""
        self._data[key] = value
        self.save()

    def get(self, key: str) -> Optional[Any]:
        """Get a configuration value."""
        return self._data.get(key)

    def save(self):
        """Save the configuration to a file."""
        with self._path.open("w") as f:
            json.dump(self._data, f, indent=4)

# Expose AppConfig object for app to import
appConfig = AppConfig()
