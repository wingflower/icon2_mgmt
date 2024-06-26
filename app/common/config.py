from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    기본 Configuration
    """
    BASE_DIR = base_dir

    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True


@dataclass
class LocalConfig(Config):
    DB_USER = "test"
    DB_PASSWD = "test"
    DB_ADDR = "mariadb"
    DB_PORT = 3306
    DB_NAME = "test"
    DB_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWD}@{DB_ADDR}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class ProdConfig(Config):
    DB_USER = "test"
    DB_PASSWD = "test"
    DB_ADDR = "mariadb"
    DB_PORT = 3306
    DB_NAME = "test"
    DB_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWD}@{DB_ADDR}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))


