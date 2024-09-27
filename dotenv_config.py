from pathlib import Path
from dotenv import load_dotenv


def l_dot_env(ENV_FILE_DIR=".env"):
    ENV_FILE_PATH = Path(ENV_FILE_DIR)
    ENV_FILE_PATH.touch(
        mode=0o600,
        exist_ok=True,
    )
    return load_dotenv(
        dotenv_path=ENV_FILE_DIR,
        override=True,
    )
