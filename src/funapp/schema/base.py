from funsecret import read_secret
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# 数据库连接串通过 funsecret 下发；未配置时使用不含凭据的本地 SQLite 数据库
_db_url = read_secret(
    "funapp",
    "mysql",
    "url",
    value="sqlite:///funapp.db",
)
engine = create_engine(_db_url)

# SQLite 只把 `INTEGER PRIMARY KEY` 当自增列，声明成 BIGINT 时自增不生效、
# 插入会撞上 `NOT NULL constraint failed`。默认连接串是本地 SQLite，所以主键
# 在 SQLite 上降级为 INTEGER，其余方言（MySQL 等）仍按 BIGINT 建表。
_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")


def create_tables() -> None:
    """创建所有表。"""
    Base.metadata.create_all(engine)


class User(Base):
    """用户账户及其基本资料。"""

    __tablename__ = "t_user"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    username = Column(String(50), unique=True)
    password = Column(String(100))
    mobile = Column(String(20), unique=True)
    email = Column(String(100), unique=True)
    nickname = Column(String(50))
    avatar_url = Column(String(255))
    user_level = Column(Integer, default=1)
    last_login_time = Column(DateTime)


class Theme(Base):
    """活动主题及展示信息。"""

    __tablename__ = "t_theme"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(50), unique=True)
    description = Column(Text)
    icon_url = Column(String(255))


class Game(Base):
    """游戏定义及默认配置。"""

    __tablename__ = "t_game"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    game_type = Column(String(50), unique=True)
    description = Column(Text)
    rules = Column(Text)
    default_config = Column(JSON)


class Campaign(Base):
    """活动定义、时间范围和关联主题。"""

    __tablename__ = "t_campaign"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100), unique=True)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    theme_id = Column(BigInteger, ForeignKey("t_theme.id"))
    max_level_count = Column(Integer, default=1)

    theme = relationship("Theme")


class GameInstance(Base):
    """活动中实际运行的游戏实例。"""

    __tablename__ = "t_game_instance"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    diff_level = Column(Integer, default=4)
    game_id = Column(BigInteger, ForeignKey("t_game.id"))
    config = Column(JSON)
    time_limit = Column(Integer)

    game = relationship("Game")


class CampaignLevel(Base):
    """活动关卡及其关联的游戏资源。"""

    __tablename__ = "t_campaign_level"

    id = Column(_PK_TYPE, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    campaign_id = Column(BigInteger, ForeignKey("t_campaign.id"))
    level_number = Column(Integer)
    game_id = Column(BigInteger, ForeignKey("t_game.id"))
    game_instance_id = Column(BigInteger, ForeignKey("t_game_instance.id"))
    reward_config = Column(JSON)

    campaign = relationship("Campaign")
    game = relationship("Game")
    game_instance = relationship("GameInstance")
